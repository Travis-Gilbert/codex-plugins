# URLSession Async Networking Patterns

## Actor-Based APIClient

```swift
actor APIClient {
    static let shared = APIClient()

    private let session: URLSession
    private let baseURL: URL
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private var authToken: String?
    private var refreshToken: String?

    init(
        baseURL: URL = URL(string: "https://api.example.com/v1")!,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.session = session

        self.decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        decoder.keyDecodingStrategy = .convertFromSnakeCase

        self.encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    func setAuth(token: String, refresh: String) {
        self.authToken = token
        self.refreshToken = refresh
    }

    func clearAuth() {
        authToken = nil
        refreshToken = nil
    }
}
```

---

## Endpoint Protocol / Enum

```swift
protocol Endpoint {
    var path: String { get }
    var method: HTTPMethod { get }
    var headers: [String: String] { get }
    var queryItems: [URLQueryItem]? { get }
    var body: (any Encodable)? { get }
    var requiresAuth: Bool { get }
}

extension Endpoint {
    var headers: [String: String] { [:] }
    var queryItems: [URLQueryItem]? { nil }
    var body: (any Encodable)? { nil }
    var requiresAuth: Bool { true }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

// Concrete endpoints
enum UserEndpoint: Endpoint {
    case profile
    case updateProfile(UpdateProfileRequest)
    case listUsers(page: Int, perPage: Int)
    case user(id: UUID)
    case deleteAccount

    var path: String {
        switch self {
        case .profile: "/me"
        case .updateProfile: "/me"
        case .listUsers: "/users"
        case .user(let id): "/users/\(id)"
        case .deleteAccount: "/me"
        }
    }

    var method: HTTPMethod {
        switch self {
        case .profile, .listUsers, .user: .get
        case .updateProfile: .patch
        case .deleteAccount: .delete
        }
    }

    var queryItems: [URLQueryItem]? {
        switch self {
        case .listUsers(let page, let perPage):
            [URLQueryItem(name: "page", value: "\(page)"),
             URLQueryItem(name: "per_page", value: "\(perPage)")]
        default: nil
        }
    }

    var body: (any Encodable)? {
        switch self {
        case .updateProfile(let request): request
        default: nil
        }
    }
}
```

---

## Generic Request Method with Typed Errors

```swift
enum AppError: Error, LocalizedError {
    case invalidURL
    case network(URLError)
    case server(statusCode: Int, message: String?)
    case decoding(DecodingError)
    case unauthorized
    case notFound
    case rateLimited(retryAfter: TimeInterval?)
    case unknown(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: "Invalid URL"
        case .network(let error): "Network error: \(error.localizedDescription)"
        case .server(let code, let msg): "Server error \(code): \(msg ?? "Unknown")"
        case .decoding: "Failed to parse server response"
        case .unauthorized: "Session expired. Please sign in again."
        case .notFound: "Resource not found"
        case .rateLimited: "Too many requests. Please wait."
        case .unknown(let error): error.localizedDescription
        }
    }
}

extension APIClient {
    func request<T: Decodable>(_ endpoint: Endpoint) async throws(AppError) -> T {
        let request: URLRequest
        do {
            request = try buildRequest(for: endpoint)
        } catch {
            throw .invalidURL
        }

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError {
            throw .network(error)
        } catch {
            throw .unknown(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw .unknown(NSError(domain: "Invalid response", code: -1))
        }

        switch httpResponse.statusCode {
        case 200...299:
            break  // Success
        case 401:
            // Attempt token refresh
            if endpoint.requiresAuth {
                return try await refreshAndRetry(endpoint)
            }
            throw .unauthorized
        case 404:
            throw .notFound
        case 429:
            let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After")
                .flatMap(TimeInterval.init)
            throw .rateLimited(retryAfter: retryAfter)
        default:
            let message = String(data: data, encoding: .utf8)
            throw .server(statusCode: httpResponse.statusCode, message: message)
        }

        do {
            return try decoder.decode(T.self, from: data)
        } catch let error as DecodingError {
            throw .decoding(error)
        } catch {
            throw .unknown(error)
        }
    }

    // Fire-and-forget (no response body)
    func send(_ endpoint: Endpoint) async throws(AppError) {
        let _: EmptyResponse = try await request(endpoint)
    }

    private func buildRequest(for endpoint: Endpoint) throws -> URLRequest {
        var components = URLComponents(url: baseURL.appendingPathComponent(endpoint.path),
                                        resolvingAgainstBaseURL: false)!
        components.queryItems = endpoint.queryItems

        guard let url = components.url else { throw AppError.invalidURL }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        for (key, value) in endpoint.headers {
            request.setValue(value, forHTTPHeaderField: key)
        }

        if endpoint.requiresAuth, let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = endpoint.body {
            request.httpBody = try encoder.encode(AnyEncodable(body))
        }

        return request
    }
}

struct EmptyResponse: Decodable {}

struct AnyEncodable: Encodable {
    private let encode: (Encoder) throws -> Void
    init(_ value: any Encodable) {
        self.encode = { encoder in try value.encode(to: encoder) }
    }
    func encode(to encoder: Encoder) throws {
        try encode(encoder)
    }
}
```

---

## JWT Token Auth with Refresh on 401

```swift
extension APIClient {
    private func refreshAndRetry<T: Decodable>(_ endpoint: Endpoint) async throws(AppError) -> T {
        guard let refreshToken else { throw .unauthorized }

        struct RefreshRequest: Encodable { let refreshToken: String }
        struct TokenResponse: Decodable {
            let accessToken: String
            let refreshToken: String
            let expiresIn: Int
        }

        // Build refresh request manually (avoid recursion)
        var refreshURL = baseURL.appendingPathComponent("/auth/refresh")
        var request = URLRequest(url: refreshURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? encoder.encode(RefreshRequest(refreshToken: refreshToken))

        do {
            let (data, response) = try await session.data(for: request)
            guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                clearAuth()
                throw AppError.unauthorized
            }
            let tokens = try decoder.decode(TokenResponse.self, from: data)
            setAuth(token: tokens.accessToken, refresh: tokens.refreshToken)

            // Store in Keychain
            try KeychainHelper.save(tokens.accessToken, for: .accessToken)
            try KeychainHelper.save(tokens.refreshToken, for: .refreshToken)

            // Retry original request
            return try await self.request(endpoint)
        } catch {
            clearAuth()
            throw .unauthorized
        }
    }
}
```

---

## Keychain Storage for Tokens

```swift
enum KeychainKey: String {
    case accessToken = "com.app.access-token"
    case refreshToken = "com.app.refresh-token"
}

enum KeychainHelper {
    static func save(_ value: String, for key: KeychainKey) throws {
        let data = Data(value.utf8)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key.rawValue,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock,
        ]

        SecItemDelete(query as CFDictionary)  // Remove existing
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.saveFailed(status)
        }
    }

    static func load(_ key: KeychainKey) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key.rawValue,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func delete(_ key: KeychainKey) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key.rawValue,
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

---

## Codable Patterns

### Custom CodingKeys

```swift
struct User: Codable {
    let id: UUID
    let fullName: String
    let emailAddress: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case fullName = "full_name"
        case emailAddress = "email"
        case createdAt = "created_at"
    }
}
```

### Global Snake Case Strategy (Preferred)

```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
// "full_name" -> fullName automatically — no CodingKeys needed
```

### Custom Date Decoding

```swift
// ISO 8601 (most APIs)
decoder.dateDecodingStrategy = .iso8601

// Custom format
decoder.dateDecodingStrategy = .custom { decoder in
    let container = try decoder.singleValueContainer()
    let string = try container.decode(String.self)

    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    if let date = formatter.date(from: string) { return date }

    // Fallback: epoch seconds
    if let epoch = Double(string) { return Date(timeIntervalSince1970: epoch) }

    throw DecodingError.dataCorrupted(
        .init(codingPath: decoder.codingPath, debugDescription: "Cannot decode date: \(string)")
    )
}
```

---

## Request Retry

```swift
extension APIClient {
    func requestWithRetry<T: Decodable>(
        _ endpoint: Endpoint,
        maxRetries: Int = 3,
        backoff: @Sendable (Int) -> Duration = { attempt in .seconds(pow(2.0, Double(attempt))) }
    ) async throws(AppError) -> T {
        var lastError: AppError = .unknown(NSError(domain: "", code: 0))

        for attempt in 0..<maxRetries {
            do {
                return try await request(endpoint)
            } catch let error as AppError {
                lastError = error
                switch error {
                case .network, .rateLimited:
                    if attempt < maxRetries - 1 {
                        try? await Task.sleep(for: backoff(attempt))
                    }
                default:
                    throw error  // Non-retryable
                }
            }
        }
        throw lastError
    }
}
```

---

## Multipart Upload

```swift
extension APIClient {
    func upload(
        fileData: Data,
        fileName: String,
        mimeType: String,
        to path: String,
        additionalFields: [String: String] = [:]
    ) async throws(AppError) -> UploadResponse {
        let boundary = UUID().uuidString
        var body = Data()

        // Additional text fields
        for (key, value) in additionalFields {
            body.append("--\(boundary)\r\n")
            body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n")
            body.append("\(value)\r\n")
        }

        // File part
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n")
        body.append("Content-Type: \(mimeType)\r\n\r\n")
        body.append(fileData)
        body.append("\r\n--\(boundary)--\r\n")

        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await session.upload(for: request, from: body)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw .server(statusCode: (response as? HTTPURLResponse)?.statusCode ?? 0, message: nil)
        }
        return try decoder.decode(UploadResponse.self, from: data)
    }
}

private extension Data {
    mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) { append(data) }
    }
}
```

---

## AsyncBytes Streaming

```swift
extension APIClient {
    func stream<T: Decodable>(
        _ endpoint: Endpoint,
        as type: T.Type
    ) -> AsyncThrowingStream<T, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    let request = try buildRequest(for: endpoint)
                    let (bytes, response) = try await session.bytes(for: request)

                    guard let http = response as? HTTPURLResponse,
                          (200...299).contains(http.statusCode) else {
                        continuation.finish(throwing: AppError.server(
                            statusCode: (response as? HTTPURLResponse)?.statusCode ?? 0,
                            message: nil
                        ))
                        return
                    }

                    // Server-Sent Events (SSE) parsing
                    var buffer = ""
                    for try await line in bytes.lines {
                        if line.hasPrefix("data: ") {
                            let json = String(line.dropFirst(6))
                            if json == "[DONE]" { break }
                            if let data = json.data(using: .utf8) {
                                let decoded = try decoder.decode(T.self, from: data)
                                continuation.yield(decoded)
                            }
                        }
                    }
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }
}

// Usage
for try await chunk in apiClient.stream(.chatCompletion(prompt), as: ChatChunk.self) {
    accumulatedText += chunk.text
}
```

---

## Usage Examples

```swift
// Fetch a user profile
let profile: UserProfile = try await APIClient.shared.request(UserEndpoint.profile)

// List with pagination
let page: PaginatedResponse<User> = try await APIClient.shared.request(
    UserEndpoint.listUsers(page: 1, perPage: 20)
)

// Update profile
let updated: UserProfile = try await APIClient.shared.request(
    UserEndpoint.updateProfile(UpdateProfileRequest(name: "New Name"))
)
```
