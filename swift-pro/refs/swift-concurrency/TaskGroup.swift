// REFERENCE: Swift TaskGroup
// withTaskGroup, withThrowingTaskGroup, structured concurrency

// ─── withTaskGroup ───────────────────────────────────────────────────
// Run multiple child tasks concurrently. All children must complete
// before the group scope exits (structured concurrency guarantee).

func fetchAllImages(urls: [URL]) async -> [URL: Image] {
    await withTaskGroup(of: (URL, Image?).self) { group in
        for url in urls {
            group.addTask {
                let image = try? await downloadImage(from: url)
                return (url, image)
            }
        }

        var results: [URL: Image] = [:]
        for await (url, image) in group {
            if let image {
                results[url] = image
            }
        }
        return results
    }
}

// ─── withThrowingTaskGroup ───────────────────────────────────────────
// Same as withTaskGroup, but child tasks can throw.
// If any child throws, the group cancels remaining children.

func fetchAllUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask {
                try await api.fetchUser(id: id)
            }
        }

        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}

// ─── addTask ─────────────────────────────────────────────────────────
// Add a child task to the group. The closure inherits the group's actor context.

await withTaskGroup(of: Void.self) { group in
    group.addTask { await processA() }
    group.addTask { await processB() }
    group.addTask { await processC() }
    // All three run concurrently; group waits for all to finish
}

// addTask with priority:
group.addTask(priority: .high) {
    await urgentWork()
}

// ─── Collecting Results ──────────────────────────────────────────────
// Iterate the group to collect results as they complete (unordered).

let results = await withTaskGroup(of: Int.self) { group in
    for i in 0..<10 {
        group.addTask { await compute(i) }
    }

    // Collect into array — results arrive in completion order, not submission order
    var collected: [Int] = []
    for await result in group {
        collected.append(result)
    }
    return collected
}

// Using reduce:
let sum = await withTaskGroup(of: Int.self) { group in
    for i in 0..<100 {
        group.addTask { await compute(i) }
    }
    return await group.reduce(0, +)
}

// ─── cancelAll ───────────────────────────────────────────────────────
// Cancel all remaining child tasks in the group.

func findFirst(in urls: [URL]) async -> Data? {
    await withTaskGroup(of: Data?.self) { group in
        for url in urls {
            group.addTask {
                try? await URLSession.shared.data(from: url).0
            }
        }

        // Return the first successful result, cancel the rest
        for await data in group {
            if data != nil {
                group.cancelAll()
                return data
            }
        }
        return nil
    }
}

// ─── waitForAll ──────────────────────────────────────────────────────
// Wait for all tasks without consuming results.
// (Just iterate to drain — or let the scope end.)

await withTaskGroup(of: Void.self) { group in
    for item in items {
        group.addTask { await process(item) }
    }
    // Implicit waitForAll when group scope exits
}

// Explicitly drain:
await withTaskGroup(of: Void.self) { group in
    for item in items {
        group.addTask { await process(item) }
    }
    await group.waitForAll()  // Explicit wait
}

// ─── Limiting Concurrency ────────────────────────────────────────────
// TaskGroup does not limit concurrency by default. Use a pattern
// to bound the number of in-flight tasks.

func processWithLimit(items: [Item], maxConcurrency: Int) async {
    await withTaskGroup(of: Void.self) { group in
        var iterator = items.makeIterator()

        // Seed the group with initial batch
        for _ in 0..<maxConcurrency {
            guard let item = iterator.next() else { break }
            group.addTask { await process(item) }
        }

        // As each completes, add the next
        for await _ in group {
            if let item = iterator.next() {
                group.addTask { await process(item) }
            }
        }
    }
}

// ─── Error Handling Patterns ─────────────────────────────────────────

// Fail-fast: first error cancels all tasks (default with throwing group)
func failFast(ids: [String]) async throws -> [Result] {
    try await withThrowingTaskGroup(of: Result.self) { group in
        for id in ids {
            group.addTask { try await fetch(id) }
        }
        var results: [Result] = []
        for try await result in group {
            results.append(result)
        }
        return results
    }
}

// Collect all, including errors:
func collectAll(ids: [String]) async -> [Swift.Result<Data, Error>] {
    await withTaskGroup(of: Swift.Result<Data, Error>.self) { group in
        for id in ids {
            group.addTask {
                do {
                    return .success(try await fetch(id))
                } catch {
                    return .failure(error)
                }
            }
        }
        var results: [Swift.Result<Data, Error>] = []
        for await result in group {
            results.append(result)
        }
        return results
    }
}
