# Push-Dirty-First Sync Engine Patterns

## Overview

A sync engine bridges local SwiftData storage with a remote API. The
"push-dirty-first" protocol ensures local changes are never overwritten by a pull.

**Core principle:** Always push local changes before pulling remote changes.

---

## isDirty Flag and Sync Bookkeeping

Every synced `@Model` carries three bookkeeping fields:

```swift
import SwiftData
import Foundation

@Model
class ContentItem {
    var title: String
    var body: String
    var createdAt: Date
    var updatedAt: Date

    // Sync bookkeeping
    var isDirty: Bool              // Local changes not yet pushed
    var lastSyncedAt: Date?        // Last successful push/pull (nil = never synced)
    var serverUpdatedAt: Date?     // Server's updatedAt from most recent pull
    var serverID: String?          // Server-side unique ID (nil = local-only)

    #Unique<ContentItem>([\.serverID])
    #Index<ContentItem>([\.isDirty], [\.serverUpdatedAt])

    init(title: String, body: String) {
        self.title = title
        self.body = body
        self.createdAt = .now
        self.updatedAt = .now
        self.isDirty = true  // new records are always dirty
    }

    func markEdited() {
        self.updatedAt = .now
        self.isDirty = true
    }

    func markSynced(serverUpdatedAt: Date) {
        self.isDirty = false
        self.lastSyncedAt = .now
        self.serverUpdatedAt = serverUpdatedAt
    }
}
```

## Why Push-Before-Pull Prevents Data Loss

Without push-first: user edits locally, pull overwrites with stale server
data, push finds nothing dirty. **Edit lost.**

With push-first: user edits locally, push sends edit to server, pull gets
latest (which now includes the edit). **Edit preserved.**

---

## SyncEngine Actor

```swift
actor SyncEngine {
    private let modelContainer: ModelContainer
    private let apiClient: APIClient
    private var isSyncing = false

    @MainActor var syncState = SyncState()

    init(modelContainer: ModelContainer, apiClient: APIClient) {
        self.modelContainer = modelContainer
        self.apiClient = apiClient
    }

    func sync() async {
        guard !isSyncing else { return }
        isSyncing = true
        defer { isSyncing = false }

        await MainActor.run { syncState.status = .syncing }

        do {
            let pushCount = try await pushDirty()
            let pullCount = try await pullAll()
            await MainActor.run {
                syncState.status = .idle
                syncState.lastSyncedAt = .now
                syncState.lastPushCount = pushCount
                syncState.lastPullCount = pullCount
                syncState.lastError = nil
            }
        } catch {
            // Leave dirty records dirty — they retry next cycle
            await MainActor.run {
                syncState.status = .error(error.localizedDescription)
                syncState.lastError = error.localizedDescription
            }
        }
    }

    @discardableResult
    private func pushDirty() async throws -> Int {
        let context = ModelContext(modelContainer)
        let dirtyItems = try context.fetch(
            FetchDescriptor<ContentItem>(predicate: #Predicate { $0.isDirty == true })
        )
        guard !dirtyItems.isEmpty else { return 0 }

        var pushCount = 0
        for item in dirtyItems {
            do {
                if let serverID = item.serverID {
                    let response = try await apiClient.updateItem(
                        id: serverID, title: item.title, body: item.body, updatedAt: item.updatedAt)
                    item.markSynced(serverUpdatedAt: response.updatedAt)
                } else {
                    let response = try await apiClient.createItem(
                        title: item.title, body: item.body,
                        createdAt: item.createdAt, updatedAt: item.updatedAt)
                    item.serverID = response.id
                    item.markSynced(serverUpdatedAt: response.updatedAt)
                }
                pushCount += 1
            } catch {
                // Individual failure: leave dirty, continue with others
                print("SyncEngine: push failed for \(item.title): \(error)")
            }
        }
        try context.save()
        return pushCount
    }

    @discardableResult
    private func pullAll() async throws -> Int {
        let context = ModelContext(modelContainer)
        let lastSync = await MainActor.run { syncState.lastSyncedAt }
        let serverItems = try await apiClient.listItems(updatedSince: lastSync)
        guard !serverItems.isEmpty else { return 0 }

        var pullCount = 0
        for serverItem in serverItems {
            let existing = try context.fetch(
                FetchDescriptor<ContentItem>(
                    predicate: #Predicate { $0.serverID == serverItem.id })
            ).first

            if let existing {
                guard !existing.isDirty else { continue }  // skip dirty — already pushed or will next cycle
                existing.title = serverItem.title
                existing.body = serverItem.body
                existing.updatedAt = serverItem.updatedAt
                existing.serverUpdatedAt = serverItem.updatedAt
                existing.lastSyncedAt = .now
            } else {
                let newItem = ContentItem(title: serverItem.title, body: serverItem.body)
                newItem.serverID = serverItem.id
                newItem.createdAt = serverItem.createdAt
                newItem.updatedAt = serverItem.updatedAt
                newItem.isDirty = false
                newItem.lastSyncedAt = .now
                newItem.serverUpdatedAt = serverItem.updatedAt
                context.insert(newItem)
            }
            pullCount += 1
        }
        try context.save()
        return pullCount
    }
}
```

---

## SyncState and Periodic Scheduling

```swift
@Observable
class SyncState {
    var status: SyncStatus = .idle
    var lastSyncedAt: Date?
    var lastPushCount: Int = 0
    var lastPullCount: Int = 0
    var lastError: String?
    var isActive: Bool { if case .syncing = status { return true }; return false }
}

enum SyncStatus: Equatable {
    case idle, syncing, error(String)
}
```

```swift
extension SyncEngine {
    func startPeriodicSync(interval: TimeInterval = 30) {
        Task { @MainActor in
            Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { [weak self] _ in
                guard let self else { return }
                Task { await self.sync() }
            }
        }
    }
}
```

### Initial Sync on App Launch

```swift
@main
struct MyApp: App {
    let container = try! ModelContainer(for: ContentItem.self)
    let syncEngine: SyncEngine

    init() {
        syncEngine = SyncEngine(modelContainer: container,
                                apiClient: APIClient(baseURL: URL(string: "https://api.example.com")!))
    }

    var body: some Scene {
        WindowGroup {
            ContentView(syncEngine: syncEngine)
                .modelContainer(container)
                .task {
                    await syncEngine.sync()
                    await syncEngine.startPeriodicSync(interval: 30)
                }
        }
    }
}
```

---

## Error Handling: Leave Dirty, Retry Next Cycle

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| Network unreachable | Catch, set `.error` status | Next timer tick retries |
| Single item push 400 | Item stays `isDirty`, others continue | Retry next cycle |
| Server 500 | Push/pull aborted | Next timer tick retries |
| Token expired 401 | APIClient refreshes, retries once | If refresh fails, prompt re-login |
| Conflict 409 | Apply resolution strategy | See below |

Dirty records act as a retry queue. No separate retry infrastructure needed.

---

## Conflict Resolution Strategies

| Strategy | How | When |
|----------|-----|------|
| Server wins (default) | Accept server if `server.updatedAt > local.serverUpdatedAt` | Multi-user, latest-write-wins |
| Local wins | Always push local | Single-user, local is truth |
| Field-level merge | Compare per-field, keep most recent | Independent document sections |
| User prompt | Surface both versions to user | Critical content |

```swift
private func resolveConflict(local: ContentItem, server: ServerItem) -> ConflictResolution {
    guard let localTimestamp = local.serverUpdatedAt else { return .pushLocal }
    if server.updatedAt > localTimestamp && local.isDirty { return .acceptServer }  // true conflict
    if server.updatedAt > localTimestamp && !local.isDirty { return .acceptServer } // no local changes
    return .pushLocal
}

enum ConflictResolution { case pushLocal, acceptServer, promptUser }
```

---

## Handling Deletions (Soft Delete)

```swift
@Model
class ContentItem {
    // ... existing fields ...
    var isDeleted: Bool = false
    var deletedAt: Date?

    func markDeleted() {
        self.isDeleted = true
        self.deletedAt = .now
        self.isDirty = true
    }
}

// In pushDirty():
if item.isDeleted {
    if let serverID = item.serverID { try await apiClient.deleteItem(id: serverID) }
    context.delete(item)
    continue
}
```

Soft delete is simpler than tombstone tables. The `isDirty` flag ensures
deletions are synced before the local record is removed.

---

## API Client Protocol for Testability

```swift
protocol SyncAPIClient: Sendable {
    func createItem(title: String, body: String, createdAt: Date, updatedAt: Date) async throws -> ServerItem
    func updateItem(id: String, title: String, body: String, updatedAt: Date) async throws -> ServerItem
    func listItems(updatedSince: Date?) async throws -> [ServerItem]
    func deleteItem(id: String) async throws
}

struct ServerItem: Codable, Sendable {
    let id: String
    let title: String
    let body: String
    let createdAt: Date
    let updatedAt: Date
}
```

Use a `MockAPIClient` conforming to this protocol for unit tests with
in-memory `ModelConfiguration(isStoredInMemoryOnly: true)`.
