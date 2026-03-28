// REFERENCE: @Test Attribute (Swift Testing)
// Test declaration, display names, tags, traits, conditional execution

import Testing

// ─── Basic @Test ─────────────────────────────────────────────────────
// Mark a function as a test with @Test. No "test" prefix required.

@Test
func additionWorks() {
    #expect(2 + 2 == 4)
}

// Async tests:
@Test
func fetchUserSucceeds() async throws {
    let user = try await api.fetchUser(id: "123")
    #expect(user.name == "Alice")
}

// ─── Display Names ───────────────────────────────────────────────────
// Provide a human-readable name shown in test results.

@Test("Addition of two positive integers")
func addPositive() {
    #expect(3 + 5 == 8)
}

@Test("User profile loads within timeout")
func profileLoad() async throws {
    let profile = try await loadProfile()
    #expect(profile != nil)
}

// ─── Tags ────────────────────────────────────────────────────────────
// Organize tests with tags for filtering and reporting.

extension Tag {
    @Tag static var networking: Self
    @Tag static var database: Self
    @Tag static var ui: Self
    @Tag static var slow: Self
    @Tag static var critical: Self
}

@Test(.tags(.networking))
func apiCallSucceeds() async throws {
    let data = try await api.fetch("/health")
    #expect(data != nil)
}

@Test(.tags(.networking, .slow))
func largeDownloadCompletes() async throws {
    let data = try await api.downloadLargeFile()
    #expect(data.count > 1_000_000)
}

// Run only tagged tests from CLI:
// swift test --filter .tags(.networking)

// ─── Traits ──────────────────────────────────────────────────────────
// Traits modify test behavior.

// Conditional execution:
@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] != nil))
func onlyOnCI() {
    // Runs only in CI environment
}

@Test(.disabled("Blocked by issue #42"))
func pendingFeature() {
    // Skipped with a reason
}

// Bug reference:
@Test(.bug("https://github.com/example/repo/issues/42", "Flaky on iOS 17"))
func sometimesFlaky() async throws {
    // Associates test with a bug tracker issue
}

// Time limit:
@Test(.timeLimit(.minutes(2)))
func longRunningOperation() async throws {
    try await performExpensiveWork()
}

// Multiple traits:
@Test(
    "Critical API endpoint responds",
    .tags(.networking, .critical),
    .timeLimit(.seconds(30)),
    .bug("https://github.com/example/repo/issues/99")
)
func criticalEndpoint() async throws {
    let response = try await api.healthCheck()
    #expect(response.status == 200)
}

// ─── Parameterized Tests ─────────────────────────────────────────────
// Run the same test with different inputs.

@Test(arguments: [1, 2, 3, 5, 8, 13])
func fibonacciNumbersArePositive(n: Int) {
    #expect(n > 0)
}

// With custom display:
@Test("Email validation", arguments: [
    ("user@example.com", true),
    ("invalid", false),
    ("a@b.c", true),
    ("@missing.com", false),
])
func emailValidation(email: String, isValid: Bool) {
    #expect(validateEmail(email) == isValid)
}

// Two-dimensional arguments (all combinations):
@Test(arguments: ["GET", "POST"], [200, 404, 500])
func handleStatusCode(method: String, statusCode: Int) {
    let response = MockResponse(method: method, statusCode: statusCode)
    #expect(response.isHandled)
}

// ─── Conditional Execution ───────────────────────────────────────────

// Skip on specific OS:
@Test(.enabled(if: {
    #if os(iOS)
    return true
    #else
    return false
    #endif
}()))
func iOSOnlyFeature() { }

// Runtime condition:
@Test(.disabled(when: isRunningInSimulator))
func requiresRealDevice() { }

// ─── Test Function Requirements ──────────────────────────────────────
// - Can be sync or async
// - Can be throwing or non-throwing
// - Must be at the top level or inside a @Suite
// - No return value
// - Parameters only for parameterized tests
