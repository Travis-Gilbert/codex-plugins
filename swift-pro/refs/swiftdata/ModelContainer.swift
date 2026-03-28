// REFERENCE: ModelContainer (SwiftData)
// Container initialization, schema config, in-memory, CloudKit

import SwiftData
import SwiftUI

// ─── Basic Initialization ────────────────────────────────────────────
// ModelContainer manages the storage backend for @Model types.

// Simplest form — single model type:
let container = try ModelContainer(for: Article.self)

// Multiple model types:
let container2 = try ModelContainer(for: Article.self, Author.self, Category.self)

// Using Schema:
let schema = Schema([Article.self, Author.self, Category.self])
let container3 = try ModelContainer(for: schema)

// ─── ModelConfiguration ──────────────────────────────────────────────
// Fine-grained control over storage behavior.

let config = ModelConfiguration(
    "MyDatabase",                   // Optional name (used for file name)
    schema: Schema([Article.self]), // Schema this config applies to
    isStoredInMemoryOnly: false,    // true for previews/tests
    allowsSave: true,               // false for read-only access
    groupContainer: .automatic      // App Group container
)

let container4 = try ModelContainer(for: Schema([Article.self]), configurations: [config])

// ─── In-Memory Store ─────────────────────────────────────────────────
// For unit tests and SwiftUI previews — no persistence.

let testConfig = ModelConfiguration(
    schema: Schema([Article.self, Author.self]),
    isStoredInMemoryOnly: true
)
let testContainer = try ModelContainer(
    for: Schema([Article.self, Author.self]),
    configurations: [testConfig]
)

// Seeding preview data:
let previewContainer: ModelContainer = {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try! ModelContainer(for: Article.self, configurations: [config])
    let context = container.mainContext

    // Insert sample data
    let article = Article(title: "Sample", body: "Preview content")
    context.insert(article)

    return container
}()

// ─── CloudKit Configuration ──────────────────────────────────────────
// Sync with CloudKit by specifying cloudKitDatabase.

let cloudConfig = ModelConfiguration(
    "CloudDatabase",
    schema: Schema([Article.self]),
    cloudKitDatabase: .automatic  // Uses default CloudKit container
)

// CloudKit database options:
//   .automatic — Uses the app's default container
//   .private("iCloud.com.example.app") — Specific container, private DB
//   .none — No CloudKit sync

// ─── Multiple Configurations ─────────────────────────────────────────
// Use separate configurations for different storage needs.

let localConfig = ModelConfiguration(
    "LocalData",
    schema: Schema([CacheEntry.self]),
    isStoredInMemoryOnly: false,
    cloudKitDatabase: .none           // Local only, no sync
)

let syncConfig = ModelConfiguration(
    "SyncedData",
    schema: Schema([UserDocument.self]),
    cloudKitDatabase: .automatic      // Synced via CloudKit
)

let multiContainer = try ModelContainer(
    for: Schema([CacheEntry.self, UserDocument.self]),
    configurations: [localConfig, syncConfig]
)

// ─── SwiftUI Integration ─────────────────────────────────────────────
// Use .modelContainer modifier on the app or scene.

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Article.self, Author.self])
        // Or with custom container:
        // .modelContainer(customContainer)
    }
}

// With configuration:
// .modelContainer(for: Article.self, inMemory: true)

// Access in views via @Environment:
struct SomeView: View {
    @Environment(\.modelContext) private var context

    var body: some View {
        Text("Has context")
    }
}

// ─── Custom Container Setup ──────────────────────────────────────────
// For complex setups, create the container in the App init.

@main
struct ProductionApp: App {
    let container: ModelContainer

    init() {
        let schema = Schema([Article.self, Author.self, Category.self])

        let config: ModelConfiguration
        #if DEBUG
        config = ModelConfiguration(schema: schema, isStoredInMemoryOnly: true)
        #else
        config = ModelConfiguration(
            "Production",
            schema: schema,
            isStoredInMemoryOnly: false,
            allowsSave: true
        )
        #endif

        do {
            container = try ModelContainer(for: schema, configurations: [config])
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}

// ─── Container Properties ────────────────────────────────────────────
// container.mainContext   — The main-actor-bound ModelContext
// container.schema        — The Schema describing all models
// container.configurations — Array of ModelConfiguration
//
// Create additional contexts for background work:
// let bgContext = ModelContext(container)
// bgContext runs on whatever actor/thread you call it from
