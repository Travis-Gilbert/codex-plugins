// REFERENCE: #expect and #require Macros (Swift Testing)
// Assertions, comparisons, error testing, boolean expectations

import Testing

// ─── #expect ─────────────────────────────────────────────────────────
// Non-fatal assertion. Test continues even if #expect fails.
// Records all failures in the test report.

@Test func basicExpectations() {
    // Boolean
    #expect(true)
    #expect(isValid(input: "hello"))

    // Equality
    #expect(2 + 2 == 4)
    #expect(user.name == "Alice")

    // Inequality
    #expect(count != 0)

    // Comparison
    #expect(score > 80)
    #expect(latency < 1.0)
    #expect(items.count >= 3)
    #expect(retries <= maxRetries)

    // Optional
    #expect(result != nil)
    #expect(optionalValue == nil)

    // String containment
    #expect(message.contains("success"))
    #expect(url.absoluteString.hasPrefix("https://"))
}

// ─── #expect with Custom Messages ────────────────────────────────────
// Add context to failure messages.

@Test func expectations() {
    let count = items.count
    #expect(count > 0, "Expected at least one item, got \(count)")

    let status = response.statusCode
    #expect(status == 200, "API returned \(status) instead of 200")
}

// ─── #expect(throws:) — Error Testing ────────────────────────────────
// Verify that code throws a specific error.

@Test func throwsSpecificError() {
    // Expect any error:
    #expect(throws: (any Error).self) {
        try riskyOperation()
    }

    // Expect a specific error type:
    #expect(throws: ValidationError.self) {
        try validate(email: "invalid")
    }

    // Expect a specific error value (Equatable errors):
    #expect(throws: AppError.unauthorized) {
        try api.fetchWithExpiredToken()
    }
}

// Verify error properties:
@Test func errorHasCorrectMessage() throws {
    let error = #expect(throws: ValidationError.self) {
        try validate(email: "")
    }
    // `error` is the thrown ValidationError — inspect it
    #expect(error.field == "email")
    #expect(error.message.contains("required"))
}

// Expect NO error thrown:
@Test func doesNotThrow() {
    #expect(throws: Never.self) {
        try safeOperation()
    }
}

// ─── #require ────────────────────────────────────────────────────────
// Fatal assertion. If #require fails, the test STOPS immediately.
// Use when subsequent code depends on this condition.

@Test func requireExample() throws {
    // Unwrap optional — test stops if nil
    let user = try #require(fetchUser(id: "123"))

    // Now safe to use `user` — guaranteed non-nil
    #expect(user.name == "Alice")
    #expect(user.email.contains("@"))
}

@Test func requireCondition() throws {
    let items = try #require(loadItems())
    try #require(!items.isEmpty, "Need at least one item to test")

    let first = items[0]
    #expect(first.isValid)
}

// #require with throws:
@Test func requireNoThrow() throws {
    let result = try #require(try parseJSON(data))
    #expect(result.count > 0)
}

// ─── Collection Expectations ─────────────────────────────────────────

@Test func collectionAssertions() {
    let numbers = [1, 2, 3, 4, 5]

    #expect(numbers.count == 5)
    #expect(numbers.contains(3))
    #expect(!numbers.isEmpty)
    #expect(numbers.first == 1)
    #expect(numbers.last == 5)
    #expect(numbers.allSatisfy { $0 > 0 })
}

// ─── Approximate Equality ────────────────────────────────────────────
// For floating-point comparisons.

@Test func floatingPoint() {
    let result = calculatePI()
    #expect(abs(result - 3.14159) < 0.001)

    // Or use a helper:
    #expect(result.isApproximatelyEqual(to: 3.14159, absoluteTolerance: 0.001))
}

// ─── Async Expectations ──────────────────────────────────────────────

@Test func asyncExpectations() async throws {
    let result = try await api.fetchData()
    #expect(result.count > 0)
    #expect(result.first?.isValid == true)
}

// ─── #expect vs #require Decision Guide ──────────────────────────────
//
// Use #expect when:
//   - You want to see ALL failures (not just the first)
//   - The assertion is independent of subsequent code
//   - Testing multiple properties of the same object
//
// Use #require when:
//   - Subsequent code would crash without this condition
//   - Unwrapping an optional needed for further assertions
//   - A precondition for the rest of the test
//
// Example:
// @Test func processItems() throws {
//     let items = try #require(loadItems())      // REQUIRE: need items to continue
//     #expect(items.count == 5)                  // EXPECT: count check is informational
//     #expect(items[0].name == "First")          // EXPECT: independent check
//     let processed = try #require(process(items)) // REQUIRE: need result to continue
//     #expect(processed.isComplete)              // EXPECT: final check
// }

// ─── Confirmation (Async Event Testing) ──────────────────────────────
// Verify that an event occurs (like XCTest expectation/fulfill).

@Test func callbackIsCalled() async {
    await confirmation { confirm in
        eventEmitter.onEvent = { event in
            #expect(event.type == .completed)
            confirm()  // Must be called exactly once
        }
        eventEmitter.start()
    }
}

// Expected count:
@Test func multipleCallbacks() async {
    await confirmation(expectedCount: 3) { confirm in
        for _ in 0..<3 {
            processor.onItem = { _ in confirm() }
        }
        processor.processAll()
    }
}
