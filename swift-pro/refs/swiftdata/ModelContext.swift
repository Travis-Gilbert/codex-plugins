// REFERENCE: ModelContext (SwiftData)
// CRUD operations, save, undo/redo, autosave, rollback

import SwiftData
import SwiftUI

// ─── Getting a ModelContext ──────────────────────────────────────────
// In SwiftUI:
struct ExampleView: View {
    @Environment(\.modelContext) private var context
    var body: some View { Text("Example") }
}

// From a container:
// let context = container.mainContext       // Main actor context
// let bgContext = ModelContext(container)    // Background context

// ─── Insert ──────────────────────────────────────────────────────────
func createArticle(context: ModelContext) {
    let article = Article(title: "New Article", body: "Content here")
    context.insert(article)
    // With autosave (default), this persists automatically
}

// Insert with relationship:
func createBookWithAuthor(context: ModelContext) {
    let author = Author(name: "Jane Doe")
    let book = Book(title: "Swift Guide", author: author)
    context.insert(author)
    context.insert(book)
}

// ─── Fetch ───────────────────────────────────────────────────────────
// FetchDescriptor defines what to fetch and how.

func fetchArticles(context: ModelContext) throws -> [Article] {
    let descriptor = FetchDescriptor<Article>(
        sortBy: [SortDescriptor(\.publishedAt, order: .reverse)]
    )
    return try context.fetch(descriptor)
}

// With predicate:
func searchArticles(query: String, context: ModelContext) throws -> [Article] {
    let predicate = #Predicate<Article> {
        $0.title.localizedStandardContains(query)
    }
    var descriptor = FetchDescriptor(predicate: predicate)
    descriptor.sortBy = [SortDescriptor(\.publishedAt, order: .reverse)]
    return try context.fetch(descriptor)
}

// With fetch limit and offset:
func fetchPage(page: Int, pageSize: Int, context: ModelContext) throws -> [Article] {
    var descriptor = FetchDescriptor<Article>(
        sortBy: [SortDescriptor(\.publishedAt, order: .reverse)]
    )
    descriptor.fetchLimit = pageSize
    descriptor.fetchOffset = page * pageSize
    return try context.fetch(descriptor)
}

// Fetch count only (efficient):
func articleCount(context: ModelContext) throws -> Int {
    let descriptor = FetchDescriptor<Article>()
    return try context.fetchCount(descriptor)
}

// Fetch identifiers only:
func articleIDs(context: ModelContext) throws -> [PersistentIdentifier] {
    let descriptor = FetchDescriptor<Article>()
    return try context.fetchIdentifiers(descriptor)
}

// ─── Delete ──────────────────────────────────────────────────────────
func deleteArticle(_ article: Article, context: ModelContext) {
    context.delete(article)
}

// Batch delete with predicate:
func deleteOldArticles(context: ModelContext) throws {
    let cutoff = Calendar.current.date(byAdding: .month, value: -6, to: .now)!
    let predicate = #Predicate<Article> { $0.publishedAt < cutoff }
    try context.delete(model: Article.self, where: predicate)
}

// Delete all of a type:
func deleteAllArticles(context: ModelContext) throws {
    try context.delete(model: Article.self)
}

// ─── Save ────────────────────────────────────────────────────────────
// Explicit save — writes pending changes to the persistent store.

func saveChanges(context: ModelContext) throws {
    if context.hasChanges {
        try context.save()
    }
}

// ─── Autosave ────────────────────────────────────────────────────────
// By default, ModelContext.autosaveEnabled = true
// The context saves automatically at appropriate times:
//   - When the app enters the background
//   - After a SwiftUI event cycle
//   - Periodically

// Disable for batch operations:
func batchImport(items: [ImportItem], context: ModelContext) throws {
    context.autosaveEnabled = false
    defer {
        context.autosaveEnabled = true
    }

    for item in items {
        let article = Article(title: item.title, body: item.body)
        context.insert(article)
    }

    try context.save()  // Single save for the whole batch
}

// ─── Undo / Redo ─────────────────────────────────────────────────────
// ModelContext has a built-in UndoManager.

func setupUndo(context: ModelContext) {
    context.undoManager = UndoManager()
}

// In SwiftUI, set on the container:
// .modelContainer(for: Article.self) // Undo is enabled by default in SwiftUI

// Undo/redo operations:
func undoLastChange(context: ModelContext) {
    context.undoManager?.undo()
}

func redoLastChange(context: ModelContext) {
    context.undoManager?.redo()
}

// Check availability:
// context.undoManager?.canUndo
// context.undoManager?.canRedo

// ─── Rollback ────────────────────────────────────────────────────────
// Discard all unsaved changes.

func discardChanges(context: ModelContext) {
    context.rollback()
}

// ─── Enumerate (Memory-Efficient) ────────────────────────────────────
// Process large datasets without loading all into memory.

func processAllArticles(context: ModelContext) throws {
    let descriptor = FetchDescriptor<Article>(
        sortBy: [SortDescriptor(\.publishedAt)]
    )

    try context.enumerate(descriptor, batchSize: 100) { article in
        // Process one article at a time
        article.viewCount += 1
    }
    // Automatically saves in batches
}

// ─── Background Context ──────────────────────────────────────────────
// Create a separate context for background work.

func importInBackground(container: ModelContainer, data: [ImportItem]) async throws {
    let context = ModelContext(container)
    // This context is NOT on the main actor

    for item in data {
        let article = Article(title: item.title, body: item.body)
        context.insert(article)
    }

    try context.save()
    // Changes are visible to mainContext after save
}

// ─── Registered Models ───────────────────────────────────────────────
// Check what the context knows about:
// context.insertedModelsArray    — Newly inserted, unsaved
// context.changedModelsArray     — Modified, unsaved
// context.deletedModelsArray     — Marked for deletion, unsaved
// context.hasChanges             — Any pending changes?
