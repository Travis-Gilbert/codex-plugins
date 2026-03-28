// REFERENCE: Swift Task API
// Task creation, detached, value, sleep, cancellation

// ─── Task Creation ───────────────────────────────────────────────────
// Task {} inherits the current actor context and priority.

func loadData() {
    Task {
        // Inherits current actor (e.g., @MainActor if called from UI)
        let data = try await fetchFromNetwork()
        updateUI(with: data)  // Safe if on @MainActor
    }
}

// With explicit priority:
Task(priority: .userInitiated) {
    await performImportantWork()
}

// Task(priority:) options:
//   .high / .userInitiated
//   .medium / .utility  (default if unspecified)
//   .low
//   .background

// ─── Task.detached ───────────────────────────────────────────────────
// Detached tasks do NOT inherit the current actor or priority.
// Use when work should run independently of the calling context.

Task.detached(priority: .background) {
    // NOT on @MainActor even if called from @MainActor context
    await processLargeDataset()
}

// ─── Task.value ──────────────────────────────────────────────────────
// Await the result of a task.

let task = Task<String, Error> {
    try await fetchUserName()
}

let name = try await task.value  // Suspends until task completes

// Non-throwing variant:
let task2 = Task<Int, Never> {
    42
}
let number = await task2.value

// ─── Task.sleep ──────────────────────────────────────────────────────
// Suspends the current task for a duration. Supports cancellation.

func pollWithDelay() async throws {
    // Sleep for 2 seconds (nanoseconds)
    try await Task.sleep(nanoseconds: 2_000_000_000)

    // Preferred: Sleep for a Duration (Swift 5.9+)
    try await Task.sleep(for: .seconds(2))
    try await Task.sleep(for: .milliseconds(500))

    // Sleep until a specific instant:
    try await Task.sleep(until: .now + .seconds(5), clock: .continuous)
}

// ─── Task Cancellation ───────────────────────────────────────────────
// Tasks support cooperative cancellation.

let longTask = Task {
    for i in 0..<1000 {
        // Check cancellation periodically
        try Task.checkCancellation()  // Throws CancellationError if cancelled

        // Or check without throwing:
        if Task.isCancelled {
            // Clean up and return early
            return
        }

        await processItem(i)
    }
}

// Cancel from outside:
longTask.cancel()

// ─── Task.checkCancellation() ────────────────────────────────────────
// Throws CancellationError if the current task is cancelled.
// Use at suspension points or at the start of expensive operations.

func fetchAllPages() async throws -> [Page] {
    var pages: [Page] = []
    var nextURL: URL? = startURL

    while let url = nextURL {
        try Task.checkCancellation()     // Bail out early if cancelled
        let (page, next) = try await fetchPage(url)
        pages.append(page)
        nextURL = next
    }

    return pages
}

// ─── withTaskCancellationHandler ─────────────────────────────────────
// Run cleanup code when a task is cancelled.
// The handler runs CONCURRENTLY with the operation — must be thread-safe.

func downloadFile(from url: URL) async throws -> Data {
    let session = URLSession.shared
    let delegate = DownloadDelegate()

    return try await withTaskCancellationHandler {
        // Main operation
        try await session.data(from: url).0
    } onCancel: {
        // Runs immediately when task is cancelled (concurrent!)
        // Must be Sendable — no captured mutable state
        delegate.cancelDownload()
    }
}

// ─── Task Local Values ───────────────────────────────────────────────
// Scoped values that propagate through the task hierarchy.

enum RequestContext {
    @TaskLocal static var requestID: String = "none"
    @TaskLocal static var traceID: String?
}

func handleRequest() async {
    await RequestContext.$requestID.withValue("req-123") {
        // All code in this scope (and child tasks) sees requestID = "req-123"
        await processRequest()
    }
}

func processRequest() async {
    print(RequestContext.requestID)  // "req-123"
}

// ─── Patterns ────────────────────────────────────────────────────────

// Fire-and-forget from synchronous context:
func buttonTapped() {
    Task { await viewModel.save() }
}

// Returning a value:
func computeResult() async -> Int {
    let task = Task { await heavyComputation() }
    return await task.value
}

// Timeout pattern:
func fetchWithTimeout() async throws -> Data {
    try await withThrowingTaskGroup(of: Data.self) { group in
        group.addTask { try await fetchData() }
        group.addTask {
            try await Task.sleep(for: .seconds(10))
            throw TimeoutError()
        }
        let result = try await group.next()!
        group.cancelAll()
        return result
    }
}
