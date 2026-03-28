// REFERENCE: @Suite Attribute (Swift Testing)
// Test organization, nested suites, shared setup

import Testing

// ─── Basic @Suite ────────────────────────────────────────────────────
// Group related tests in a struct (or class/actor/enum).

@Suite
struct MathTests {
    @Test func addition() {
        #expect(2 + 3 == 5)
    }

    @Test func subtraction() {
        #expect(10 - 4 == 6)
    }

    @Test func multiplication() {
        #expect(3 * 7 == 21)
    }
}

// ─── @Suite with Display Name ────────────────────────────────────────

@Suite("User Authentication")
struct AuthTests {
    @Test("Valid credentials succeed")
    func validLogin() async throws {
        let result = try await auth.login(user: "alice", pass: "secret")
        #expect(result.isAuthenticated)
    }

    @Test("Invalid password fails")
    func invalidPassword() async throws {
        #expect(throws: AuthError.invalidCredentials) {
            try await auth.login(user: "alice", pass: "wrong")
        }
    }
}

// ─── Nested Suites ───────────────────────────────────────────────────
// Nest structs for hierarchical organization.

@Suite("API Client")
struct APIClientTests {

    @Suite("GET Requests")
    struct GetTests {
        @Test func fetchUser() async throws {
            let user = try await client.get("/users/1")
            #expect(user != nil)
        }

        @Test func fetchNotFound() async throws {
            #expect(throws: APIError.notFound) {
                try await client.get("/users/999")
            }
        }
    }

    @Suite("POST Requests")
    struct PostTests {
        @Test func createUser() async throws {
            let user = try await client.post("/users", body: newUserData)
            #expect(user.id != nil)
        }

        @Test func createWithInvalidData() async throws {
            #expect(throws: APIError.validationFailed) {
                try await client.post("/users", body: invalidData)
            }
        }
    }
}

// ─── Shared Setup (init) ─────────────────────────────────────────────
// Use the suite struct's init for setup. Each test gets a fresh instance.

@Suite("Database Operations")
struct DatabaseTests {
    let db: TestDatabase

    init() async throws {
        // Runs BEFORE each test
        db = try await TestDatabase.createInMemory()
        try await db.seed(with: .sampleData)
    }

    @Test func fetchAllRecords() async throws {
        let records = try await db.fetchAll()
        #expect(records.count == 10)  // From seed data
    }

    @Test func insertRecord() async throws {
        try await db.insert(Record(name: "New"))
        let count = try await db.count()
        #expect(count == 11)  // 10 seeded + 1 new
    }

    // Each test starts with a fresh db — insertRecord doesn't affect fetchAllRecords
}

// ─── Shared Setup with Properties ────────────────────────────────────

@Suite("Cart Operations")
struct CartTests {
    let cart: ShoppingCart
    let sampleProduct: Product

    init() {
        cart = ShoppingCart()
        sampleProduct = Product(id: "p1", name: "Widget", price: 9.99)
        cart.add(sampleProduct)
    }

    @Test func cartHasOneItem() {
        #expect(cart.items.count == 1)
    }

    @Test func cartTotalIsCorrect() {
        #expect(cart.total == 9.99)
    }

    @Test func removeItem() {
        cart.remove(sampleProduct)
        #expect(cart.items.isEmpty)
    }
}

// ─── Suite Traits ────────────────────────────────────────────────────
// Traits on @Suite apply to all contained tests.

@Suite("Integration Tests", .tags(.networking), .serialized)
struct IntegrationTests {
    // All tests: tagged .networking, run sequentially

    @Test func connectToServer() async throws { }
    @Test func authenticateSession() async throws { }
    @Test func fetchProtectedResource() async throws { }
}

// ─── .serialized ─────────────────────────────────────────────────────
// Force sequential execution within a suite.
// By default, tests run in parallel.

@Suite(.serialized)
struct OrderedTests {
    // Tests run one at a time, in declaration order
    @Test func step1_setup() { }
    @Test func step2_execute() { }
    @Test func step3_verify() { }
}

// ─── Suites with Actors ──────────────────────────────────────────────
// Use an actor-based suite for tests that share mutable state safely.

@Suite("Counter Tests")
struct CounterTests {
    @Test func increment() {
        var counter = Counter()
        counter.increment()
        #expect(counter.value == 1)
    }

    @Test func decrement() {
        var counter = Counter(value: 5)
        counter.decrement()
        #expect(counter.value == 4)
    }
}

// ─── Enum-Based Suites ───────────────────────────────────────────────
// Use enums as namespaces (no instances, just grouping).

@Suite("String Utilities")
enum StringUtilTests {
    @Test static func trimming() {
        #expect("  hello  ".trimmed == "hello")
    }

    @Test static func capitalizing() {
        #expect("hello world".titleCased == "Hello World")
    }
}

// ─── Test Organization Best Practices ────────────────────────────────
//
// 1. One suite per feature or module
// 2. Nest suites for sub-features
// 3. Use display names for readability
// 4. Put setup in init, not in each test
// 5. Use .serialized only when tests truly depend on order
// 6. Use tags for cross-cutting concerns (slow, network, etc.)
// 7. Keep each test focused on one behavior
