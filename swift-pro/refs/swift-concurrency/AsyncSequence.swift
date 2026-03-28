// REFERENCE: AsyncSequence, AsyncStream, AsyncThrowingStream
// Async iteration, stream creation, operators

// ─── AsyncSequence Protocol ──────────────────────────────────────────
// AsyncSequence produces elements asynchronously, one at a time.
// Conforms to: protocol AsyncSequence where Element: Sendable

// Consuming with for-await-in:
func processNotifications(_ notifications: some AsyncSequence<Notification, Never>) async {
    for await notification in notifications {
        handle(notification)
    }
}

// Built-in AsyncSequences:
// - URL.resourceBytes            → AsyncBytes
// - URLSession.bytes(from:)      → (AsyncBytes, URLResponse)
// - FileHandle.bytes             → AsyncBytes
// - NotificationCenter.notifications(named:) → AsyncSequence

// Example: reading URL bytes
func countBytes(from url: URL) async throws -> Int {
    var count = 0
    for try await _ in url.resourceBytes {
        count += 1
    }
    return count
}

// ─── AsyncStream ─────────────────────────────────────────────────────
// Bridge callback-based or delegate APIs into async sequences.

// Basic creation with continuation:
let stream = AsyncStream<Int> { continuation in
    for i in 0..<10 {
        continuation.yield(i)
    }
    continuation.finish()
}

// Consuming:
for await value in stream {
    print(value)
}

// Bridging a delegate/callback pattern:
func locationUpdates() -> AsyncStream<CLLocation> {
    AsyncStream { continuation in
        let manager = CLLocationManager()
        let delegate = LocationDelegate { location in
            continuation.yield(location)
        }
        manager.delegate = delegate

        continuation.onTermination = { _ in
            manager.stopUpdatingLocation()
        }

        manager.startUpdatingLocation()
    }
}

// With buffering policy:
let buffered = AsyncStream<Event>(bufferingPolicy: .bufferingNewest(10)) { continuation in
    // Only keeps the 10 most recent events if consumer is slow
    eventSource.onEvent = { event in
        continuation.yield(event)
    }
}

// Buffering policies:
//   .unbounded          — No limit (default), may grow without bound
//   .bufferingOldest(n) — Keep first n, drop new when full
//   .bufferingNewest(n) — Keep last n, drop old when full

// ─── AsyncThrowingStream ─────────────────────────────────────────────
// Same as AsyncStream but can throw errors.

func eventStream() -> AsyncThrowingStream<Event, Error> {
    AsyncThrowingStream { continuation in
        let connection = WebSocket(url: serverURL)

        connection.onMessage = { message in
            do {
                let event = try JSONDecoder().decode(Event.self, from: message)
                continuation.yield(event)
            } catch {
                continuation.finish(throwing: error)
            }
        }

        connection.onClose = { reason in
            if let error = reason.error {
                continuation.finish(throwing: error)
            } else {
                continuation.finish()
            }
        }

        continuation.onTermination = { _ in
            connection.close()
        }

        connection.connect()
    }
}

// Consuming throwing streams:
do {
    for try await event in eventStream() {
        process(event)
    }
} catch {
    handleStreamError(error)
}

// ─── AsyncSequence Operators ─────────────────────────────────────────
// Familiar functional operators, but async.

// map
let names = users.map { $0.name }
// for await name in names { ... }

// compactMap — filters nil
let validScores = rawScores.compactMap { Int($0) }

// filter
let adults = people.filter { $0.age >= 18 }

// prefix — take first n elements
let firstFive = notifications.prefix(5)

// prefix(while:) — take while predicate holds
let untilError = events.prefix { $0.isValid }

// drop(while:) — skip elements while predicate holds
let afterWarmup = readings.drop { $0.temperature < threshold }

// reduce
let total = await values.reduce(0, +)

// contains
let hasError = await events.contains { $0.isError }

// first(where:)
let firstMatch = await items.first { $0.id == targetID }

// min / max (requires Comparable elements)
let lowest = await temperatures.min()

// Chaining:
func processStream(_ events: some AsyncSequence<Event, Error>) async throws {
    for try await event in events
        .filter { $0.isImportant }
        .prefix(100)
        .map { $0.payload }
    {
        await handle(event)
    }
}

// ─── Making a Custom AsyncSequence ───────────────────────────────────

struct Counter: AsyncSequence {
    typealias Element = Int
    let limit: Int

    struct AsyncIterator: AsyncIteratorProtocol {
        let limit: Int
        var current = 0

        mutating func next() async -> Int? {
            guard current < limit else { return nil }
            defer { current += 1 }
            return current
        }
    }

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(limit: limit)
    }
}

// Usage:
// for await n in Counter(limit: 10) { print(n) }
