# Networking Layer Template -- URLSession + Async/Await

## Directory Structure

```
Networking/
  APIClient.swift       # Actor-isolated HTTP client
  Endpoint.swift        # Endpoint protocol and route definitions
  AuthManager.swift     # JWT token management and refresh
  AppError.swift        # Typed error hierarchy
  JSONDecoder+App.swift # Preconfigured decoder
```

## APIClient.swift

```swift
import Foundation

actor APIClient {
    static let shared = APIClient()

    private let session: URLSession
    private let decoder: JSONDecoder
    private let authManager: AuthManager

    init(
        session: URLSession = .shared,
        decoder: JSONDecoder = .appDefault,
        authManager: AuthManager = .shared
    ) {
        self.session = session
        self.decoder = decoder
        self.authManager = authManager
    }

    // MARK: - Public

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let urlRequest = try await buildRequest(for: endpoint)
        let (data, response) = try await session.data(for: urlRequest)
        try validate(response)
        return try decoder.decode(T.self, from: data)
    }

    func request(_ endpoint: Endpoint) async throws {
        let urlRequest = try await buildRequest(for: endpoint)
        let (_, response) = try await session.data(for: urlRequest)
        try validate(response)
    }

    // MARK: - Private

    private func buildRequest(for endpoint: Endpoint) async throws -> URLRequest {
        guard let url = endpoint.url else {
            throw AppError.invalidURL(endpoint.path)
        }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.allHTTPHeaderFields = endpoint.headers

        if endpoint.requiresAuth {
            let token = try await authManager.validToken()
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = endpoint.body {
            request.httpBody = try JSONEncoder().encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }

        return request
    }

    private func validate(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else {
            throw AppError.invalidResponse
        }
        switch http.statusCode {
        case 200...299: return
        case 401:       throw AppError.unauthorized
        case 403:       throw AppError.forbidden
        case 404:       throw AppError.notFound
        case 429:       throw AppError.rateLimited
        case 500...599: throw AppError.serverError(http.statusCode)
        default:        throw AppError.httpError(http.statusCode)
        }
    }
}
```

## Endpoint.swift

```swift
import Foundation

enum HTTPMethod: String {
    case GET, POST, PUT, PATCH, DELETE
}

protocol Endpoint {
    var baseURL: String { get }
    var path: String { get }
    var method: HTTPMethod { get }
    var headers: [String: String] { get }
    var queryItems: [URLQueryItem]? { get }
    var body: (any Encodable)? { get }
    var requiresAuth: Bool { get }
}

extension Endpoint {
    var baseURL: String { "https://api.example.com/v1" }
    var headers: [String: String] { ["Accept": "application/json"] }
    var queryItems: [URLQueryItem]? { nil }
    var body: (any Encodable)? { nil }
    var requiresAuth: Bool { true }

    var url: URL? {
        var components = URLComponents(string: baseURL + path)
        components?.queryItems = queryItems
        return components?.url
    }
}

// Example usage:
//
// enum UserEndpoint: Endpoint {
//     case list
//     case detail(id: String)
//     case create(body: CreateUserRequest)
//
//     var path: String {
//         switch self {
//         case .list:          "/users"
//         case .detail(let id): "/users/\(id)"
//         case .create:        "/users"
//         }
//     }
//
//     var method: HTTPMethod {
//         switch self {
//         case .list, .detail: .GET
//         case .create:        .POST
//         }
//     }
//
//     var body: (any Encodable)? {
//         switch self {
//         case .create(let body): body
//         default: nil
//         }
//     }
// }
```

## AuthManager.swift

```swift
import Foundation

actor AuthManager {
    static let shared = AuthManager()

    private var accessToken: String?
    private var refreshToken: String?
    private var expiresAt: Date?
    private var refreshTask: Task<String, Error>?

    func validToken() async throws -> String {
        // Return existing token if still valid
        if let token = accessToken, let exp = expiresAt, exp > Date.now.addingTimeInterval(30) {
            return token
        }

        // Deduplicate concurrent refresh calls
        if let task = refreshTask {
            return try await task.value
        }

        let task = Task<String, Error> {
            defer { refreshTask = nil }
            return try await performRefresh()
        }
        refreshTask = task
        return try await task.value
    }

    func setTokens(access: String, refresh: String, expiresIn: TimeInterval) {
        self.accessToken = access
        self.refreshToken = refresh
        self.expiresAt = Date.now.addingTimeInterval(expiresIn)
    }

    func clearTokens() {
        accessToken = nil
        refreshToken = nil
        expiresAt = nil
    }

    private func performRefresh() async throws -> String {
        guard let refresh = refreshToken else {
            throw AppError.unauthorized
        }

        var request = URLRequest(url: URL(string: "https://api.example.com/v1/auth/refresh")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(["refresh_token": refresh])

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            clearTokens()
            throw AppError.unauthorized
        }

        struct TokenResponse: Decodable {
            let accessToken: String
            let refreshToken: String
            let expiresIn: TimeInterval
        }

        let tokens = try JSONDecoder.appDefault.decode(TokenResponse.self, from: data)
        setTokens(access: tokens.accessToken, refresh: tokens.refreshToken, expiresIn: tokens.expiresIn)
        return tokens.accessToken
    }
}
```

## AppError.swift

```swift
import Foundation

enum AppError: LocalizedError {
    case invalidURL(String)
    case invalidResponse
    case unauthorized
    case forbidden
    case notFound
    case rateLimited
    case serverError(Int)
    case httpError(Int)
    case decodingFailed(Error)
    case networkUnavailable
    case custom(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL(let path):     "Invalid URL: \(path)"
        case .invalidResponse:          "Invalid server response"
        case .unauthorized:             "Session expired. Please sign in again."
        case .forbidden:                "You do not have permission for this action."
        case .notFound:                 "The requested resource was not found."
        case .rateLimited:              "Too many requests. Please try again later."
        case .serverError(let code):    "Server error (\(code)). Please try again."
        case .httpError(let code):      "Request failed with status \(code)."
        case .decodingFailed(let err):  "Data parsing error: \(err.localizedDescription)"
        case .networkUnavailable:       "No internet connection."
        case .custom(let message):      message
        }
    }
}
```

## JSONDecoder+App.swift

```swift
import Foundation

extension JSONDecoder {
    static let appDefault: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let string = try container.decode(String.self)

            if let date = ISO8601DateFormatter().date(from: string) {
                return date
            }

            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
            formatter.locale = Locale(identifier: "en_US_POSIX")
            if let date = formatter.date(from: string) {
                return date
            }

            throw DecodingError.dataCorrupted(
                .init(codingPath: decoder.codingPath, debugDescription: "Unrecognized date format: \(string)")
            )
        }
        return decoder
    }()
}
```
