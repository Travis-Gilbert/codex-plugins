// REFERENCE: SwiftData Schema Versioning and Migration
// VersionedSchema, SchemaMigrationPlan, MigrationStage

import SwiftData

// ─── Schema Basics ───────────────────────────────────────────────────
// Schema describes the model types managed by a ModelContainer.

let schema = Schema([Article.self, Author.self, Category.self])

// Schema with version:
let versionedSchema = Schema([Article.self], version: Schema.Version(1, 0, 0))

// ─── VersionedSchema ─────────────────────────────────────────────────
// Define each schema version as a separate enum conforming to VersionedSchema.
// Each version contains the model definitions AS THEY WERE at that version.

// Version 1: Initial schema
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)

    static var models: [any PersistentModel.Type] {
        [NoteV1.self]
    }

    @Model
    final class NoteV1 {
        var title: String
        var content: String
        var createdAt: Date

        init(title: String, content: String) {
            self.title = title
            self.content = content
            self.createdAt = .now
        }
    }
}

// Version 2: Added isPinned and tags
enum SchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)

    static var models: [any PersistentModel.Type] {
        [NoteV2.self, TagV2.self]
    }

    @Model
    final class NoteV2 {
        var title: String
        var content: String
        var createdAt: Date
        var isPinned: Bool           // NEW in V2
        var tags: [TagV2]            // NEW in V2

        init(title: String, content: String) {
            self.title = title
            self.content = content
            self.createdAt = .now
            self.isPinned = false
            self.tags = []
        }
    }

    @Model
    final class TagV2 {              // NEW model in V2
        var name: String
        var notes: [NoteV2]

        init(name: String) {
            self.name = name
            self.notes = []
        }
    }
}

// Version 3: Renamed content to body, added updatedAt
enum SchemaV3: VersionedSchema {
    static var versionIdentifier = Schema.Version(3, 0, 0)

    static var models: [any PersistentModel.Type] {
        [Note.self, Tag.self]
    }

    // These are the CURRENT production models
    @Model
    final class Note {
        var title: String
        var body: String             // RENAMED from content in V3
        var createdAt: Date
        var updatedAt: Date          // NEW in V3
        var isPinned: Bool
        var tags: [Tag]

        init(title: String, body: String) {
            self.title = title
            self.body = body
            self.createdAt = .now
            self.updatedAt = .now
            self.isPinned = false
            self.tags = []
        }
    }

    @Model
    final class Tag {
        var name: String
        var notes: [Note]

        init(name: String) {
            self.name = name
            self.notes = []
        }
    }
}

// ─── SchemaMigrationPlan ─────────────────────────────────────────────
// Defines the ordered list of schemas and migration stages.

enum NoteMigrationPlan: SchemaMigrationPlan {
    // List ALL schema versions in order (oldest to newest)
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self, SchemaV3.self]
    }

    // Define migration stages between consecutive versions
    static var stages: [MigrationStage] {
        [migrateV1toV2, migrateV2toV3]
    }

    // V1 → V2: Adding properties with defaults (lightweight)
    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: SchemaV1.self,
        toVersion: SchemaV2.self
    )

    // V2 → V3: Renaming a property (custom migration required)
    static let migrateV2toV3 = MigrationStage.custom(
        fromVersion: SchemaV2.self,
        toVersion: SchemaV3.self,
        willMigrate: { context in
            // Pre-migration: runs before schema change
            // Access OLD model types here
        },
        didMigrate: { context in
            // Post-migration: runs after schema change
            // Access NEW model types here
            let notes = try context.fetch(FetchDescriptor<SchemaV3.Note>())
            for note in notes {
                note.updatedAt = note.createdAt  // Set default for new property
            }
            try context.save()
        }
    )
}

// ─── MigrationStage Types ────────────────────────────────────────────

// Lightweight migration — automatic, no code needed:
//   - Adding a new property with a default value
//   - Adding a new model type
//   - Removing a property
//   - Adding an optional property (defaults to nil)
let lightweight = MigrationStage.lightweight(
    fromVersion: SchemaV1.self,
    toVersion: SchemaV2.self
)

// Custom migration — manual data transformation:
//   - Renaming a property
//   - Changing a property type
//   - Computing new values from old data
//   - Merging or splitting models
let custom = MigrationStage.custom(
    fromVersion: SchemaV2.self,
    toVersion: SchemaV3.self,
    willMigrate: nil,       // Optional: before schema change
    didMigrate: { context in // Optional: after schema change
        // Transform data here
        try context.save()
    }
)

// ─── Using the Migration Plan ────────────────────────────────────────
// Pass the migration plan when creating the container.

let container = try ModelContainer(
    for: SchemaV3.Note.self, SchemaV3.Tag.self,
    migrationPlan: NoteMigrationPlan.self
)

// In SwiftUI:
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(
            for: [SchemaV3.Note.self, SchemaV3.Tag.self],
            migrationPlan: NoteMigrationPlan.self
        )
    }
}

// ─── Migration Best Practices ────────────────────────────────────────
//
// 1. NEVER modify old VersionedSchema enums after shipping.
//    They represent the schema at a point in time.
//
// 2. Always add new versions at the END of the schemas array.
//
// 3. Test migrations with real data before shipping:
//    - Create a test with V1 data, migrate to V2, verify
//    - Test skip migrations (V1 → V3) — SwiftData runs stages in order
//
// 4. Keep migration stages small and focused.
//
// 5. Use lightweight migration whenever possible.
//
// 6. Back up user data before destructive migrations.
//
// 7. The current production models should match the LATEST VersionedSchema.
