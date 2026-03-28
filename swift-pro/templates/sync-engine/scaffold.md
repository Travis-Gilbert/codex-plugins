# Sync Engine Scaffold

> Background sync with isDirty tracking and push-dirty-first protocol.

## SyncEngine Actor

```swift
import SwiftData
import Foundation

actor SyncEngine {
    private let api: APIClient
    private let modelContext: ModelContext

    init(api: APIClient, modelContext: ModelContext) {
        self.api = api
        self.modelContext = modelContext
    }

    // The correct order: push first, then pull.
    func sync() async {
        do {
            try await pushDirty()
            try await pullAll()
        } catch {
            // Log error, retry next cycle. Do not crash.
            print("Sync failed: \(error)")
        }
    }

    func pushDirty() async throws {
        let descriptor = FetchDescriptor<ContentItem>(
            predicate: #Predicate { $0.isDirty == true }
        )
        let dirtyItems = try modelContext.fetch(descriptor)

        for item in dirtyItems {
            let saved = try await api.save(item)
            item.serverUpdatedAt = saved.updatedAt
            item.isDirty = false
            item.lastSyncedAt = Date()
        }
        try modelContext.save()
    }

    func pullAll() async throws {
        let serverItems = try await api.fetchAll()

        for apiItem in serverItems {
            let descriptor = FetchDescriptor<ContentItem>(
                predicate: #Predicate { $0.id == apiItem.id }
            )
            let existing = try modelContext.fetch(descriptor).first

            if let local = existing {
                if local.isDirty {
                    // Conflict: server wins only if newer
                    if apiItem.updatedAt > local.updatedAt {
                        local.update(from: apiItem)
                        local.isDirty = false
                    }
                    // else: local wins, will push next cycle
                } else {
                    local.update(from: apiItem)
                }
            } else {
                modelContext.insert(ContentItem.from(apiItem))
            }
        }
        try modelContext.save()
    }
}
```

## Syncable @Model Template

```swift
@Model
final class ContentItem {
    @Attribute(.unique) var id: String
    var title: String
    var body: String
    var updatedAt: Date

    // Sync bookkeeping (every syncable model gets these)
    var isDirty: Bool = false
    var lastSyncedAt: Date?
    var serverUpdatedAt: Date?

    // Call this on every local edit
    func markDirty() {
        isDirty = true
        updatedAt = Date()
    }

    func update(from api: APIContentItem) {
        title = api.title
        body = api.body
        updatedAt = api.updatedAt
        serverUpdatedAt = api.updatedAt
        lastSyncedAt = Date()
    }

    static func from(_ api: APIContentItem) -> ContentItem {
        let item = ContentItem()
        item.id = api.id
        item.title = api.title
        item.body = api.body
        item.updatedAt = api.updatedAt
        item.serverUpdatedAt = api.updatedAt
        item.lastSyncedAt = Date()
        item.isDirty = false
        return item
    }
}
```

## Periodic Sync Scheduling

```swift
// In the @main App struct
@main
struct MyApp: App {
    let container = try! ModelContainer(for: ContentItem.self)

    var body: some Scene {
        WindowGroup {
            ContentView()
                .task {
                    let engine = SyncEngine(
                        api: APIClient.shared,
                        modelContext: container.mainContext
                    )
                    await engine.sync()  // Initial sync

                    // Periodic sync every 30 seconds
                    Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { _ in
                        Task { await engine.sync() }
                    }
                }
        }
        .modelContainer(container)
    }
}
```

## Conflict Resolution Strategies

| Strategy | When to Use |
|----------|------------|
| Server wins | Default for most models (compare timestamps) |
| Local wins | Single-user apps, active editing |
| Field merge | Collaborative editing (compare per-field) |
| User prompt | High-stakes conflicts (present both versions) |
