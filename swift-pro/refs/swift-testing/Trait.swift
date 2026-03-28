// REFERENCE: Swift Testing Traits
// .enabled, .disabled, .timeLimit, .bug, custom traits

import Testing

// ─── .enabled(if:) ──────────────────────────────────────────────────
// Run test only when condition is true. Otherwise, test is SKIPPED (not failed).

@Test(.enabled(if: ProcessInfo.processInfo.environment["API_KEY"] != nil))
func requiresAPIKey() async throws {
    let key = ProcessInfo.processInfo.environment["API_KEY"]!
    let result = try await api.authenticate(key: key)
    #expect(result.isValid)
}

// With a static boolean:
@Test(.enabled(if: FeatureFlags.newSearchEnabled))
func newSearchReturnsResults() async throws {
    let results = try await search.query("test")
    #expect(!results.isEmpty)
}

// Platform-specific:
#if canImport(UIKit)
let hasUIKit = true
#else
let hasUIKit = false
#endif

@Test(.enabled(if: hasUIKit))
func uiKitSnapshot() {
    // Only runs on platforms with UIKit
}

// ─── .disabled(when:) / .disabled(_:) ────────────────────────────────
// Skip with a reason string.

@Test(.disabled("Waiting for backend deploy — ETA March 30"))
func newEndpoint() async throws {
    // Skipped — shows reason in test output
}

// Conditional disable:
@Test(.disabled(when: isCI, "Flaky in CI, investigating"))
func flakyNetworkTest() async throws {
    // Skipped in CI, runs locally
}

// ─── .timeLimit ──────────────────────────────────────────────────────
// Fail the test if it exceeds the time limit.

@Test(.timeLimit(.seconds(5)))
func quickResponse() async throws {
    let response = try await api.ping()
    #expect(response.latency < 1.0)
}

@Test(.timeLimit(.minutes(1)))
func importLargeDataset() async throws {
    try await importer.importAll()
}

// Available units:
//   .seconds(n)
//   .minutes(n)

// ─── .bug ────────────────────────────────────────────────────────────
// Associate a test with a bug tracker issue.

@Test(.bug("https://github.com/example/repo/issues/42"))
func workaroundForBug42() {
    // Documents that this test covers a known bug
}

@Test(.bug("https://jira.example.com/browse/PROJ-123", "Null pointer in parser"))
func parserHandlesNullInput() {
    let result = parser.parse(nil)
    #expect(result == .empty)
}

// Multiple bugs:
@Test(
    .bug("https://github.com/example/repo/issues/10"),
    .bug("https://github.com/example/repo/issues/15", "Related regression")
)
func complexEdgeCase() { }

// ─── .serialized ─────────────────────────────────────────────────────
// Force tests in a suite to run one at a time (not parallel).

@Suite(.serialized)
struct DatabaseTests {
    @Test func createRecord() async throws { }
    @Test func updateRecord() async throws { }
    @Test func deleteRecord() async throws { }
    // These run sequentially, not concurrently
}

// ─── Combining Traits ────────────────────────────────────────────────
// Pass multiple traits as arguments.

@Test(
    "Critical payment flow",
    .tags(.critical, .networking),
    .timeLimit(.seconds(30)),
    .bug("https://github.com/example/repo/issues/99"),
    .enabled(if: ProcessInfo.processInfo.environment["STRIPE_KEY"] != nil)
)
func processPayment() async throws {
    let result = try await paymentService.charge(amount: 1000)
    #expect(result.status == .succeeded)
}

// ─── Custom Traits ───────────────────────────────────────────────────
// Define reusable trait configurations.

// Custom trait via extension:
extension Trait where Self == Testing.ConditionTrait {
    /// Only run on devices with at least 4GB RAM
    static var requiresHighMemory: Self {
        .enabled(if: ProcessInfo.processInfo.physicalMemory >= 4_000_000_000)
    }
}

@Test(.requiresHighMemory)
func processLargeImage() async throws {
    // Skipped on low-memory devices
}

// ─── Suite-Level Traits ──────────────────────────────────────────────
// Traits on @Suite apply to all tests in the suite.

@Suite("Network Integration", .tags(.networking), .timeLimit(.minutes(2)))
struct NetworkIntegrationTests {
    // All tests inherit .networking tag and 2-minute timeout

    @Test func fetchUsers() async throws { }
    @Test func fetchPosts() async throws { }

    // Individual tests can add more traits:
    @Test(.tags(.slow))
    func fetchLargeDataset() async throws { }
    // This test has both .networking (from suite) and .slow
}
