# Swift 6 Strict Concurrency

## Enabling Strict Concurrency Checking

Swift 6 enforces data-race safety at compile time. Enable strict checking progressively:

```swift
// Package.swift — per-target
.target(
    name: "MyApp",
    swiftSettings: [
        .enableExperimentalFeature("StrictConcurrency")  // Swift 5.10
        // In Swift 6, strict concurrency is the default language mode
    ]
)

// Or set the language mode explicitly
.target(
    name: "MyApp",
    swiftSettings: [
        .swiftLanguageMode(.v6)
    ]
)
```

In Xcode: Build Settings > Swift Compiler - Upcoming Features > Strict Concurrency Checking = Complete.

For migration, use `.enableUpcomingFeature("StrictConcurrency")` in Swift 5.10 to preview warnings before adopting Swift 6.

---

## Sendable Protocol

`Sendable` marks types safe to share across concurrency domains.

```swift
// Value types are implicitly Sendable when all stored properties are Sendable
struct UserProfile: Sendable {
    let id: UUID
    let name: String
    var score: Int  // Int is Sendable
}

// Classes must be final and have only immutable Sendable stored properties
final class CacheKey: Sendable {
    let identifier: String
    let timestamp: Date

    init(identifier: String, timestamp: Date) {
        self.identifier = identifier
        self.timestamp = timestamp
    }
}

// Enums with Sendable associated values are implicitly Sendable
enum NetworkResult: Sendable {
    case success(Data)
    case failure(String)
}

// Mark unchecked when you guarantee safety manually
class LegacyCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Any] = [:]

    func get(_ key: String) -> Any? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}
```

### Sendable Conformance Rules

| Type | Sendable When |
|------|---------------|
| `struct` | All stored properties are `Sendable` (implicit conformance) |
| `enum` | All associated values are `Sendable` (implicit conformance) |
| `final class` | All stored properties are immutable (`let`) and `Sendable` |
| Non-final `class` | Cannot conform to `Sendable` (subclasses could add mutable state) |
| `actor` | Always `Sendable` (isolation guarantees safety) |
| Tuples | `Sendable` when all elements are `Sendable` |
| Functions | Only `@Sendable` closures are `Sendable` |

---

## @Sendable Closures

Closures crossing isolation boundaries must be `@Sendable`:

```swift
// @Sendable closures cannot capture mutable local state
func processItems(_ items: [Item]) async {
    // OK: captures immutable value
    let threshold = 10
    let filtered = await withTaskGroup(of: Item?.self) { group in
        for item in items {
            group.addTask { // implicitly @Sendable
                item.score > threshold ? item : nil
            }
        }
        return await group.reduce(into: []) { result, item in
            if let item { result.append(item) }
        }
    }
}

// Explicit @Sendable annotation
let completion: @Sendable (Result<Data, Error>) -> Void = { result in
    // Cannot capture mutable variables from enclosing scope
}

// Common with DispatchQueue
DispatchQueue.global().async { @Sendable in
    // work here
}
```

---

## Actor Isolation

Actors protect mutable state with serial access:

```swift
actor BankAccount {
    let id: UUID
    private(set) var balance: Decimal

    init(id: UUID, initialBalance: Decimal) {
        self.id = id
        self.balance = initialBalance
    }

    func deposit(_ amount: Decimal) {
        balance += amount
    }

    func withdraw(_ amount: Decimal) throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }
        balance -= amount
    }

    // nonisolated — accessible without await, cannot touch mutable state
    nonisolated var description: String {
        "Account(\(id))"  // Only accesses `let` property
    }
}

// All actor method calls require await from outside
let account = BankAccount(id: UUID(), initialBalance: 1000)
try await account.withdraw(500)
let currentBalance = await account.balance
```

### Isolation Boundaries

```swift
actor DataStore {
    var items: [Item] = []

    // Returning non-Sendable types across isolation boundaries is an error
    // BAD: func getItems() -> [Item]  // if Item is not Sendable

    // GOOD: return Sendable types or copy data
    func getItemCount() -> Int { items.count }
    func getItemIDs() -> [UUID] { items.map(\.id) }
}
```

---

## @MainActor

### Type-Level Annotation

```swift
// All properties and methods are main-actor-isolated
@MainActor
final class ProfileViewModel: Observable {
    var name: String = ""
    var isLoading: Bool = false

    func loadProfile() async {
        isLoading = true  // Runs on main actor
        let profile = await APIClient.shared.fetchProfile()
        name = profile.name  // Still on main actor
        isLoading = false
    }
}
```

### Method-Level Annotation

```swift
class NetworkService {
    func fetchData() async throws -> Data {
        // Runs on caller's executor
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }

    @MainActor
    func updateUI(with data: Data) {
        // Guaranteed main thread
    }
}
```

### Opting Out Within @MainActor Type

```swift
@MainActor
class ViewModel {
    var title: String = ""

    nonisolated func computeHash() -> String {
        // Can run anywhere — cannot access `title`
        return SHA256.hash(data: Data()).description
    }
}
```

---

## Global Actors

```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
class DatabaseManager {
    private var connection: Connection?

    func execute(_ query: String) async throws -> [Row] {
        // Serialized on DatabaseActor
        guard let connection else { throw DBError.notConnected }
        return try await connection.execute(query)
    }
}

// Isolate individual functions
class MixedService {
    @MainActor func refreshUI() { /* ... */ }
    @DatabaseActor func saveRecord() async throws { /* ... */ }
}
```

---

## Structured Concurrency

### async let

```swift
func loadDashboard() async throws -> Dashboard {
    async let profile = fetchProfile()
    async let notifications = fetchNotifications()
    async let settings = fetchSettings()

    // All three run concurrently; awaited together
    return try await Dashboard(
        profile: profile,
        notifications: notifications,
        settings: settings
    )
    // If any throws, the others are automatically cancelled
}
```

### TaskGroup

```swift
func downloadImages(urls: [URL]) async throws -> [UIImage] {
    try await withThrowingTaskGroup(of: (Int, UIImage).self) { group in
        for (index, url) in urls.enumerated() {
            group.addTask {
                let (data, _) = try await URLSession.shared.data(from: url)
                guard let image = UIImage(data: data) else {
                    throw ImageError.invalidData
                }
                return (index, image)
            }
        }

        var images = [(Int, UIImage)]()
        for try await result in group {
            images.append(result)
        }
        return images.sorted(by: { $0.0 < $1.0 }).map(\.1)
    }
}

// Limiting concurrency
func processInBatches(_ items: [Item], maxConcurrency: Int = 4) async throws {
    try await withThrowingTaskGroup(of: Void.self) { group in
        var iterator = items.makeIterator()

        // Start initial batch
        for _ in 0..<maxConcurrency {
            guard let item = iterator.next() else { break }
            group.addTask { try await self.process(item) }
        }

        // As each finishes, start the next
        for try await _ in group {
            if let item = iterator.next() {
                group.addTask { try await self.process(item) }
            }
        }
    }
}
```

---

## Unstructured Concurrency

### Task {}

Inherits actor isolation and priority from the enclosing context:

```swift
@MainActor
class ViewController: UIViewController {
    func userTappedRefresh() {
        Task {
            // Inherits @MainActor isolation
            showLoadingSpinner()
            let data = try await fetchData()  // Suspends, not on main thread
            updateUI(with: data)  // Back on main actor
        }
    }
}
```

### Task.detached

No inheritance of isolation or priority:

```swift
func startBackgroundSync() {
    Task.detached(priority: .utility) {
        // NOT on any actor — fully independent
        await self.performSync()  // Must await if calling actor-isolated methods
    }
}
```

### When to Use Which

| Pattern | Use When |
|---------|----------|
| `async let` | Fixed number of concurrent operations, all needed |
| `TaskGroup` | Dynamic number of concurrent operations |
| `Task {}` | Fire-and-forget from sync context, keep actor isolation |
| `Task.detached` | Truly independent work, no inherited context needed |

---

## Cancellation

```swift
func downloadLargeFile(url: URL) async throws -> Data {
    var accumulated = Data()
    let (bytes, _) = try await URLSession.shared.bytes(from: url)

    for try await byte in bytes {
        // Check cancellation periodically
        try Task.checkCancellation()
        accumulated.append(byte)
    }
    return accumulated
}

// Cooperative cancellation
func processStream() async {
    while !Task.isCancelled {
        guard let next = await stream.next() else { break }
        await process(next)
    }
    // Cleanup after cancellation
    await cleanup()
}

// withTaskCancellationHandler for bridging callbacks
func fetchWithCancellation() async throws -> Data {
    let request = buildRequest()
    return try await withTaskCancellationHandler {
        try await performRequest(request)
    } onCancel: {
        request.cancel()  // Called immediately on cancellation
    }
}
```

---

## Common Warnings and Fixes

| Warning / Error | Cause | Fix |
|----------------|-------|-----|
| `Sending 'value' risks data race` | Non-Sendable value crosses isolation boundary | Make the type `Sendable`, use `@unchecked Sendable`, or restructure |
| `Capture of 'self' with non-sendable type in @Sendable closure` | Capturing non-Sendable `self` in Task/async | Make the enclosing type an `actor` or `@MainActor` class |
| `Actor-isolated property cannot be referenced from non-isolated context` | Accessing actor state without `await` | Add `await`, or mark accessor `nonisolated` if it only reads `let` properties |
| `Non-sendable type returned by implicitly async call` | Returning non-Sendable from cross-actor call | Return a `Sendable` type or copy data into a `Sendable` wrapper |
| `Global variable is not concurrency-safe` | Mutable global/static variable | Use `actor`, `nonisolated(unsafe)`, or wrap in a `Sendable` container |
| `Main actor-isolated property cannot be mutated from non-isolated context` | Writing to @MainActor property from background | Wrap mutation in `await MainActor.run { }` or `Task { @MainActor in }` |
| `Cannot pass function of type '@Sendable () -> Void' to non-sendable parameter` | API expects non-Sendable closure | Annotate your closure `@Sendable` or mark the parameter |
| `Task-isolated value of type 'X' passed as Sendable` | Passing task-local non-Sendable value out | Use `sending` parameter annotation (Swift 6) or make type Sendable |

### The `sending` Keyword (Swift 6)

```swift
// `sending` promises the caller won't use the value after passing it
func enqueue(_ item: sending Item) async {
    await processor.handle(item)
}
```

### nonisolated(unsafe) for Legacy Globals

```swift
// Use sparingly — for genuinely thread-safe globals (e.g., immutable after init)
nonisolated(unsafe) let sharedFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateStyle = .medium
    return f
}()
```
