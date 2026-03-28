// REFERENCE: Swift Actors
// Actor declaration, isolation rules, nonisolated, reentrancy

// ─── Actor Declaration ───────────────────────────────────────────────
// Actors are reference types with built-in serialized access.
// All stored properties and methods are isolated by default.

actor BankAccount {
    let id: String              // let properties are safe to access from anywhere
    var balance: Double         // var properties are actor-isolated

    init(id: String, balance: Double) {
        self.id = id
        self.balance = balance
    }

    // Isolated method — callers must await
    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) throws {
        guard balance >= amount else {
            throw AccountError.insufficientFunds
        }
        balance -= amount
    }
}

// Calling from outside:
// let account = BankAccount(id: "123", balance: 100)
// await account.deposit(50)
// let current = await account.balance

// ─── Actor Isolation Rules ───────────────────────────────────────────
// 1. Only one task executes on an actor at a time (serial execution).
// 2. Cross-actor access requires `await`.
// 3. Actors can freely call their own methods synchronously (within the actor).
// 4. `let` properties can be read without await (they are Sendable and immutable).

// ─── nonisolated ─────────────────────────────────────────────────────
// Mark methods/properties that don't need actor isolation.
// Useful for conforming to protocols or exposing safe computed values.

actor UserCache {
    let name: String          // Already nonisolated (let)
    var entries: [String: Any] = [:]

    // nonisolated: can be called without await
    nonisolated var displayName: String {
        name.uppercased()     // Only accesses `let` property — safe
    }

    // nonisolated conformance to Hashable
    nonisolated func hash(into hasher: inout Hasher) {
        hasher.combine(name)
    }

    // Cannot access `entries` from a nonisolated context:
    // nonisolated func broken() -> Int {
    //     entries.count  // ERROR: actor-isolated property
    // }
}

// ─── Actor Reentrancy ────────────────────────────────────────────────
// Actors are reentrant: when a method hits an `await` suspension point,
// other tasks can execute on the actor. State may change across awaits.

actor ImageDownloader {
    private var cache: [URL: Image] = [:]

    func image(for url: URL) async throws -> Image {
        // Check cache BEFORE suspension
        if let cached = cache[url] {
            return cached
        }

        // ⚠️ Suspension point — another task may run here
        let image = try await downloadImage(from: url)

        // Check again AFTER suspension — another task may have cached it
        if let cached = cache[url] {
            return cached
        }

        cache[url] = image
        return image
    }
}

// ─── Global Actors ───────────────────────────────────────────────────
// @globalActor defines a singleton actor that any declaration can opt into.

@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

// Annotate functions or types to run on the global actor:
@DatabaseActor
func saveToDisk(_ data: Data) { /* runs on DatabaseActor */ }

@DatabaseActor
final class DatabaseManager {
    var connection: Connection?
    func query(_ sql: String) -> [Row] { /* ... */ [] }
}

// ─── Sendable Conformance ────────────────────────────────────────────
// Actors implicitly conform to Sendable (safe to share across concurrency domains).
// Their isolated state is protected by serialized access.

// You can pass actor references freely between tasks:
// Task { await account.deposit(100) }
// Task { await account.withdraw(50) }
