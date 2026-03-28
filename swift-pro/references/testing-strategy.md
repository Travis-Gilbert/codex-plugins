# Swift Testing Strategy

## Swift Testing Framework

Swift Testing (available in Xcode 16+) replaces XCTest for unit and integration tests. Use XCTest only for UI tests.

### @Test and @Suite

```swift
import Testing

@Suite("UserService Tests")
struct UserServiceTests {
    let service: UserService
    let mockAPI: MockAPIClient

    init() {
        mockAPI = MockAPIClient()
        service = UserService(api: mockAPI)
    }

    @Test("fetches user profile successfully")
    func fetchProfile() async throws {
        // Given
        let expected = User(id: UUID(), name: "Alice", email: "alice@example.com")
        mockAPI.stubbedResponse = expected

        // When
        let user = try await service.fetchProfile()

        // Then
        #expect(user.name == "Alice")
        #expect(user.email == "alice@example.com")
    }

    @Test("throws unauthorized when token expired")
    func expiredToken() async {
        mockAPI.stubbedError = .unauthorized

        await #expect(throws: AppError.unauthorized) {
            try await service.fetchProfile()
        }
    }
}
```

### #expect and #require

```swift
@Test func basicAssertions() {
    let value = 42

    // Boolean checks
    #expect(value == 42)
    #expect(value > 0)
    #expect(value != 0)

    // Optional checks
    let name: String? = "Alice"
    #expect(name != nil)

    // String contains
    let message = "Hello, World!"
    #expect(message.contains("World"))

    // Collection checks
    let items = [1, 2, 3]
    #expect(items.count == 3)
    #expect(items.contains(2))
    #expect(!items.isEmpty)
}

@Test func requireUnwraps() throws {
    let data: Data? = "hello".data(using: .utf8)

    // #require unwraps or fails the test immediately
    let unwrapped = try #require(data)
    #expect(unwrapped.count == 5)

    // Useful for setup that must succeed
    let user = try #require(User.from(json: sampleJSON))
    #expect(user.name == "Alice")
}

@Test func errorChecking() async throws {
    // Expect specific error type
    #expect(throws: ValidationError.self) {
        try validate(email: "not-an-email")
    }

    // Expect specific error value
    #expect(throws: ValidationError.tooShort) {
        try validate(password: "ab")
    }

    // Expect no error
    #expect(throws: Never.self) {
        try validate(email: "valid@email.com")
    }
}
```

### Traits

```swift
// Disabled test
@Test(.disabled("Waiting for API v2 deployment"))
func newAPIEndpoint() async throws {
    // ...
}

// Conditional execution
@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] != nil))
func integrationTest() async throws {
    // Only runs in CI
}

// Time limit
@Test(.timeLimit(.minutes(1)))
func longRunningOperation() async throws {
    // Fails if exceeds 1 minute
}

// Bug reference
@Test(.bug("https://github.com/org/repo/issues/123", "Flaky on CI"))
func flakyTest() async throws {
    // ...
}

// Combine traits
@Test(
    "processes large dataset",
    .timeLimit(.minutes(2)),
    .tags(.performance)
)
func largeDataset() async throws {
    // ...
}
```

### Parameterized Tests

```swift
@Test("validates email format", arguments: [
    ("alice@example.com", true),
    ("bob@test.org", true),
    ("invalid", false),
    ("@no-local.com", false),
    ("no-domain@", false),
    ("spaces in@email.com", false),
])
func emailValidation(email: String, isValid: Bool) {
    #expect(EmailValidator.isValid(email) == isValid)
}

// Multiple argument sources
@Test(arguments: ["USD", "EUR", "GBP"], [100, 0, -50])
func formatCurrency(code: String, amount: Int) {
    let result = CurrencyFormatter.format(amount: amount, code: code)
    #expect(!result.isEmpty)
}

// Enum cases
enum UserRole: CaseIterable { case admin, editor, viewer }

@Test("all roles have display names", arguments: UserRole.allCases)
func roleDisplayNames(role: UserRole) {
    #expect(!role.displayName.isEmpty)
}
```

### Tags

```swift
extension Tag {
    @Tag static var networking: Self
    @Tag static var database: Self
    @Tag static var performance: Self
    @Tag static var integration: Self
}

@Test(.tags(.networking))
func apiRequestTest() async throws { /* ... */ }

@Test(.tags(.database))
func persistenceTest() throws { /* ... */ }

@Test(.tags(.networking, .integration))
func endToEndTest() async throws { /* ... */ }

// Run specific tags from command line:
// swift test --filter tag:networking
```

---

## XCTest for UI Tests Only

```swift
import XCTest

final class OnboardingUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func testOnboardingFlow() throws {
        // Screen 1
        XCTAssert(app.staticTexts["Welcome"].exists)
        app.buttons["Get Started"].tap()

        // Screen 2
        XCTAssert(app.staticTexts["Choose Your Interests"].waitForExistence(timeout: 2))
        app.buttons["Technology"].tap()
        app.buttons["Science"].tap()
        app.buttons["Continue"].tap()

        // Screen 3
        XCTAssert(app.staticTexts["All Set!"].waitForExistence(timeout: 2))
        app.buttons["Start Exploring"].tap()

        // Verify we reached the main screen
        XCTAssert(app.navigationBars["Home"].waitForExistence(timeout: 3))
    }

    func testLoginValidation() throws {
        app.textFields["Email"].tap()
        app.textFields["Email"].typeText("invalid-email")
        app.secureTextFields["Password"].tap()
        app.secureTextFields["Password"].typeText("short")
        app.buttons["Sign In"].tap()

        XCTAssert(app.staticTexts["Invalid email address"].exists)
    }
}
```

---

## Test Architecture (Given/When/Then)

```swift
@Suite("ShoppingCart Tests")
struct ShoppingCartTests {
    @Test("adds item and updates total")
    func addItem() throws {
        // Given
        let cart = ShoppingCart()
        let product = Product(name: "Widget", price: 9.99)

        // When
        cart.add(product, quantity: 2)

        // Then
        #expect(cart.items.count == 1)
        #expect(cart.items.first?.quantity == 2)
        #expect(cart.total == 19.98)
    }

    @Test("applies percentage discount")
    func percentageDiscount() throws {
        // Given
        let cart = ShoppingCart()
        cart.add(Product(name: "Item", price: 100), quantity: 1)

        // When
        try cart.applyDiscount(.percentage(20))

        // Then
        #expect(cart.total == 80.00)
        #expect(cart.discountAmount == 20.00)
    }

    @Test("rejects expired discount code")
    func expiredDiscount() {
        // Given
        let cart = ShoppingCart()
        let expired = DiscountCode(code: "OLD20", type: .percentage(20),
                                    expiresAt: Date.distantPast)

        // When/Then
        #expect(throws: CartError.discountExpired) {
            try cart.applyDiscount(expired)
        }
    }
}
```

---

## Mock Protocols for Dependency Injection

```swift
// Define protocol
protocol UserRepositoryProtocol: Sendable {
    func fetch(id: UUID) async throws -> User
    func save(_ user: User) async throws
    func delete(id: UUID) async throws
    func list(page: Int) async throws -> [User]
}

// Production implementation
final class UserRepository: UserRepositoryProtocol {
    private let api: APIClient
    init(api: APIClient) { self.api = api }

    func fetch(id: UUID) async throws -> User {
        try await api.request(UserEndpoint.user(id: id))
    }
    // ... etc
}

// Mock for tests
final class MockUserRepository: UserRepositoryProtocol {
    var users: [UUID: User] = [:]
    var fetchCallCount = 0
    var saveCallCount = 0
    var shouldThrow = false
    var thrownError: Error = TestError.mock

    func fetch(id: UUID) async throws -> User {
        fetchCallCount += 1
        if shouldThrow { throw thrownError }
        guard let user = users[id] else { throw AppError.notFound }
        return user
    }

    func save(_ user: User) async throws {
        saveCallCount += 1
        if shouldThrow { throw thrownError }
        users[user.id] = user
    }

    func delete(id: UUID) async throws {
        if shouldThrow { throw thrownError }
        users.removeValue(forKey: id)
    }

    func list(page: Int) async throws -> [User] {
        if shouldThrow { throw thrownError }
        return Array(users.values)
    }
}

// Usage in tests
@Suite struct UserViewModelTests {
    let mock = MockUserRepository()

    @Test func loadsUser() async throws {
        let user = User(id: UUID(), name: "Test")
        mock.users[user.id] = user

        let vm = UserViewModel(repository: mock)
        await vm.loadUser(id: user.id)

        #expect(vm.user?.name == "Test")
        #expect(mock.fetchCallCount == 1)
    }
}
```

---

## Async Test Patterns

```swift
@Test func asyncOperation() async throws {
    let service = DataService()
    let result = try await service.fetchData()
    #expect(!result.isEmpty)
}

@Test func concurrentOperations() async throws {
    let service = DataService()
    async let first = service.fetchItem(id: 1)
    async let second = service.fetchItem(id: 2)

    let (item1, item2) = try await (first, second)
    #expect(item1.id != item2.id)
}

@Test(.timeLimit(.seconds(5)))
func streamProcessing() async throws {
    let stream = DataStream()
    var collected: [DataPoint] = []

    for await point in stream.values.prefix(10) {
        collected.append(point)
    }

    #expect(collected.count == 10)
}
```

---

## Test Naming Conventions

| Pattern | Example |
|---------|---------|
| Descriptive sentence | `@Test("fetches user profile successfully")` |
| Behavior-focused | `@Test("returns empty array when no results match")` |
| Edge case | `@Test("handles nil date gracefully")` |
| Error case | `@Test("throws notFound for invalid ID")` |

Avoid: `testFetchUser`, `test1`, `testSuccess`. Use natural language in the string parameter.

---

## Test Organization

```
Tests/
├── UnitTests/
│   ├── ViewModels/
│   │   ├── TaskListViewModelTests.swift
│   │   └── ProfileViewModelTests.swift
│   ├── Services/
│   │   ├── AuthServiceTests.swift
│   │   └── NetworkServiceTests.swift
│   ├── Models/
│   │   ├── UserTests.swift
│   │   └── CartTests.swift
│   └── Mocks/
│       ├── MockAPIClient.swift
│       └── MockUserRepository.swift
├── IntegrationTests/
│   ├── APIIntegrationTests.swift
│   └── DatabaseIntegrationTests.swift
└── UITests/
    ├── OnboardingUITests.swift
    └── CheckoutUITests.swift
```

### Test Pyramid

```
        /\
       /  \          UI Tests (few, slow, brittle)
      /    \         XCTest + XCUIApplication
     /------\
    /        \       Integration Tests (some)
   /          \      Swift Testing, real dependencies
  /------------\
 /              \    Unit Tests (many, fast, stable)
/                \   Swift Testing, mocked dependencies
------------------
```

---

## Performance Testing

```swift
// Swift Testing does not have built-in performance measurement
// Use XCTest for performance baselines

import XCTest

final class PerformanceTests: XCTestCase {
    func testSortingPerformance() {
        let data = (0..<10_000).map { _ in Int.random(in: 0..<100_000) }

        measure {
            _ = data.sorted()
        }
    }

    func testJSONDecodingPerformance() {
        let jsonData = generateLargeJSON(itemCount: 1000)

        measure(metrics: [XCTClockMetric(), XCTMemoryMetric()]) {
            _ = try? JSONDecoder().decode([Item].self, from: jsonData)
        }
    }
}

// Or use Swift Testing with manual timing
@Test(.tags(.performance))
func sortPerformance() {
    let data = (0..<10_000).map { _ in Int.random(in: 0..<100_000) }
    let start = ContinuousClock.now
    _ = data.sorted()
    let elapsed = ContinuousClock.now - start
    #expect(elapsed < .seconds(1))
}
```

---

## Code Coverage

Enable in Xcode: Scheme > Test > Options > Code Coverage.

From command line:
```bash
swift test --enable-code-coverage
# Results in .build/debug/codecov/
xcrun llvm-cov report .build/debug/MyAppPackageTests.xctest/Contents/MacOS/MyAppPackageTests \
    --instr-profile .build/debug/codecov/default.profdata
```

Target: 80%+ for business logic, 60%+ overall. Do not aim for 100% -- test behavior, not implementation.
