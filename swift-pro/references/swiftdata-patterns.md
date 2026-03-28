# SwiftData Framework Patterns

## @Model Macro

The `@Model` macro transforms a Swift class into a persistent model:

```swift
import SwiftData

@Model
class Book {
    // Stored properties — automatically persisted
    var title: String
    var author: String
    var publishedDate: Date
    var pageCount: Int
    var rating: Double?
    var isbn: String
    var coverImageData: Data?
    var tags: [String]  // Collections of value types are supported

    // Computed properties — NOT persisted
    var isHighlyRated: Bool { (rating ?? 0) >= 4.0 }

    // Transient properties — excluded from persistence
    @Transient var searchScore: Int = 0

    // Unique constraint
    #Unique<Book>([\.isbn])

    // Indexed for query performance
    #Index<Book>([\.title], [\.author], [\.publishedDate])

    init(title: String, author: String, publishedDate: Date, pageCount: Int, isbn: String) {
        self.title = title
        self.author = author
        self.publishedDate = publishedDate
        self.pageCount = pageCount
        self.isbn = isbn
        self.tags = []
    }
}
```

### Property Types Supported

| Type | Supported | Notes |
|------|-----------|-------|
| `String`, `Int`, `Double`, `Bool` | Yes | Primitive value types |
| `Date`, `UUID`, `URL`, `Data` | Yes | Foundation types |
| `Optional<T>` | Yes | Any supported `T` |
| `[T]` (Array) | Yes | Collections of value types |
| `[String: T]` (Dict) | Yes | Dictionary with String keys |
| `Codable` structs | Yes | Stored as encoded data |
| `enum` (RawRepresentable + Codable) | Yes | Must be Codable |
| Other `@Model` classes | Yes | Relationships (see below) |

```swift
// Codable enum support
enum ReadingStatus: String, Codable {
    case wantToRead, reading, finished, abandoned
}

@Model
class Book {
    var status: ReadingStatus = .wantToRead
}
```

---

## Relationships

### One-to-One

```swift
@Model
class UserProfile {
    var name: String
    var settings: UserSettings?  // Optional one-to-one

    init(name: String) { self.name = name }
}

@Model
class UserSettings {
    var theme: String
    var notificationsEnabled: Bool

    // Inverse relationship
    var profile: UserProfile?

    init(theme: String = "system", notificationsEnabled: Bool = true) {
        self.theme = theme
        self.notificationsEnabled = notificationsEnabled
    }
}
```

### One-to-Many

```swift
@Model
class Library {
    var name: String

    // One library has many books
    @Relationship(deleteRule: .cascade)
    var books: [Book] = []

    init(name: String) { self.name = name }
}

@Model
class Book {
    var title: String

    // Inverse: each book belongs to one library
    var library: Library?

    init(title: String) { self.title = title }
}
```

### Many-to-Many

```swift
@Model
class Student {
    var name: String

    @Relationship
    var courses: [Course] = []

    init(name: String) { self.name = name }
}

@Model
class Course {
    var title: String

    @Relationship(inverse: \Student.courses)
    var students: [Student] = []

    init(title: String) { self.title = title }
}
```

### Delete Rules

| Rule | Behavior |
|------|----------|
| `.nullify` (default) | Set relationship to nil; related objects persist |
| `.cascade` | Delete related objects when parent is deleted |
| `.deny` | Prevent deletion if related objects exist |
| `.noAction` | Do nothing (may leave orphans) |

---

## @Query Property Wrapper

### Basic Query

```swift
struct BookListView: View {
    @Query var books: [Book]

    var body: some View {
        List(books) { book in
            BookRow(book: book)
        }
    }
}
```

### Sorting

```swift
struct BookListView: View {
    @Query(sort: \.title)
    var books: [Book]

    // Multiple sort descriptors
    @Query(sort: [
        SortDescriptor(\.author),
        SortDescriptor(\.title)
    ])
    var booksByAuthor: [Book]

    // Descending
    @Query(sort: \.publishedDate, order: .reverse)
    var recentBooks: [Book]
}
```

### Filtering with #Predicate

```swift
struct HighRatedBooksView: View {
    @Query(
        filter: #Predicate<Book> { book in
            book.rating != nil && book.rating! >= 4.0
        },
        sort: \.title
    )
    var highRatedBooks: [Book]
}

// Dynamic filtering — use init parameter
struct FilteredBookList: View {
    @Query var books: [Book]

    init(author: String, minRating: Double) {
        _books = Query(
            filter: #Predicate<Book> { book in
                book.author == author &&
                (book.rating ?? 0) >= minRating
            },
            sort: \.title
        )
    }

    var body: some View {
        List(books) { book in
            BookRow(book: book)
        }
    }
}

// Complex predicates
let searchText = "Swift"
let predicate = #Predicate<Book> { book in
    book.title.localizedStandardContains(searchText) ||
    book.author.localizedStandardContains(searchText)
}
```

### Animated Query Results

```swift
@Query(sort: \.title, animation: .default)
var books: [Book]
```

### Fetch Limit

```swift
@Query(sort: \.publishedDate, order: .reverse)
var recentBooks: [Book]

init() {
    _recentBooks = Query(
        FetchDescriptor<Book>(
            sortBy: [SortDescriptor(\.publishedDate, order: .reverse)]
        ).fetchLimit(10)
    )
}
```

---

## ModelContainer Configuration

### Basic Setup

```swift
@main
struct BookApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Book.self, Library.self])
    }
}
```

### Custom Configuration

```swift
@main
struct BookApp: App {
    let container: ModelContainer

    init() {
        let schema = Schema([Book.self, Library.self, UserProfile.self])
        let config = ModelConfiguration(
            "BookDatabase",
            schema: schema,
            isStoredInMemoryOnly: false,
            allowsSave: true,
            groupContainer: .identifier("group.com.app.books"),  // App Groups
            cloudKitDatabase: .private("iCloud.com.app.books")
        )

        do {
            container = try ModelContainer(for: schema, configurations: [config])
        } catch {
            fatalError("Failed to create container: \(error)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

### In-Memory for Previews

```swift
#Preview {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try! ModelContainer(for: Book.self, configurations: config)

    // Seed preview data
    let context = container.mainContext
    context.insert(Book(title: "Sample", author: "Author", publishedDate: .now, pageCount: 200, isbn: "123"))

    return BookListView()
        .modelContainer(container)
}
```

---

## ModelContext Operations

### Insert

```swift
struct AddBookView: View {
    @Environment(\.modelContext) private var context

    func addBook() {
        let book = Book(
            title: "New Book",
            author: "Author",
            publishedDate: .now,
            pageCount: 300,
            isbn: UUID().uuidString
        )
        context.insert(book)
        // SwiftData autosaves by default
    }
}
```

### Delete

```swift
func deleteBook(_ book: Book) {
    context.delete(book)
}

// Delete with predicate
func deleteAllFinished() throws {
    try context.delete(
        model: Book.self,
        where: #Predicate { $0.status == .finished }
    )
}
```

### Fetch

```swift
func fetchBooks(by author: String) throws -> [Book] {
    let descriptor = FetchDescriptor<Book>(
        predicate: #Predicate { $0.author == author },
        sortBy: [SortDescriptor(\.title)]
    )
    return try context.fetch(descriptor)
}

// Count without fetching
func countUnread() throws -> Int {
    let descriptor = FetchDescriptor<Book>(
        predicate: #Predicate { $0.status == .wantToRead }
    )
    return try context.fetchCount(descriptor)
}

// Fetch by ID
func findBook(id: PersistentIdentifier) -> Book? {
    context.registeredModel(for: id)
}
```

### Manual Save

```swift
// Disable autosave
let container = try ModelContainer(
    for: Book.self,
    configurations: ModelConfiguration(allowsSave: true)
)
container.mainContext.autosaveEnabled = false

// Save explicitly
try context.save()
```

### Background Context

```swift
func importBooks(_ data: [BookDTO]) async throws {
    let container = self.container
    try await Task.detached {
        let context = ModelContext(container)
        for dto in data {
            let book = Book(
                title: dto.title,
                author: dto.author,
                publishedDate: dto.date,
                pageCount: dto.pages,
                isbn: dto.isbn
            )
            context.insert(book)
        }
        try context.save()
    }.value
}
```

---

## Schema Versioning and Migration

### Lightweight Migration (Automatic)

Adding new optional properties or properties with defaults requires no migration code:

```swift
// Version 1
@Model class Book {
    var title: String
    var author: String
}

// Version 2 — automatic migration
@Model class Book {
    var title: String
    var author: String
    var pageCount: Int = 0        // New with default
    var coverURL: URL?            // New optional
}
```

### Staged Migration (Manual)

For renames, type changes, or data transforms:

```swift
enum BookSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Book.self] }

    @Model class Book {
        var title: String
        var authorName: String  // Will be renamed
        init(title: String, authorName: String) {
            self.title = title
            self.authorName = authorName
        }
    }
}

enum BookSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Book.self] }

    @Model class Book {
        var title: String
        var author: String  // Renamed from authorName
        init(title: String, author: String) {
            self.title = title
            self.author = author
        }
    }
}

enum BookMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [BookSchemaV1.self, BookSchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    static let migrateV1toV2 = MigrationStage.custom(
        fromVersion: BookSchemaV1.self,
        toVersion: BookSchemaV2.self
    ) { context in
        // Fetch all books and transform
        let books = try context.fetch(FetchDescriptor<BookSchemaV1.Book>())
        for book in books {
            // Data transformation logic
        }
        try context.save()
    }
}

// Apply migration plan
let container = try ModelContainer(
    for: BookSchemaV2.Book.self,
    migrationPlan: BookMigrationPlan.self
)
```

---

## CloudKit Sync Setup

### 1. Enable Capabilities

In Xcode: Target > Signing & Capabilities > + iCloud > Check CloudKit.

### 2. Configure ModelContainer

```swift
let config = ModelConfiguration(
    cloudKitDatabase: .private("iCloud.com.yourapp.container")
)
let container = try ModelContainer(for: Book.self, configurations: config)
```

### 3. CloudKit Constraints

| Requirement | Details |
|-------------|---------|
| Optional properties | All properties must be optional or have defaults |
| No unique constraints | `#Unique` not supported with CloudKit |
| Indexed properties | Recommended for query performance |
| Relationship delete rules | `.nullify` preferred over `.cascade` |
| Value types only | No transformable attributes |

```swift
// CloudKit-compatible model
@Model
class Book {
    var title: String = ""
    var author: String = ""
    var publishedDate: Date = Date.distantPast
    var rating: Double?
    var tags: [String] = []

    @Relationship(deleteRule: .nullify)
    var library: Library?

    init(title: String, author: String) {
        self.title = title
        self.author = author
    }
}
```

### 4. Handling Sync Status

```swift
// Monitor for remote changes
NotificationCenter.default.addObserver(
    forName: ModelContext.willSave,
    object: nil,
    queue: .main
) { notification in
    // Handle incoming remote changes
}
```

---

## Common Patterns

### Repository Pattern

```swift
@Observable
class BookRepository {
    private let context: ModelContext

    init(context: ModelContext) {
        self.context = context
    }

    func all(sortedBy sort: SortDescriptor<Book>...) throws -> [Book] {
        let descriptor = FetchDescriptor<Book>(sortBy: sort)
        return try context.fetch(descriptor)
    }

    func find(isbn: String) throws -> Book? {
        let descriptor = FetchDescriptor<Book>(
            predicate: #Predicate { $0.isbn == isbn }
        )
        return try context.fetch(descriptor).first
    }

    func save(_ book: Book) throws {
        context.insert(book)
        try context.save()
    }

    func remove(_ book: Book) throws {
        context.delete(book)
        try context.save()
    }
}
```

### Undo/Redo Support

```swift
@main
struct BookApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: Book.self) { result in
            if case .success(let container) = result {
                container.mainContext.undoManager = UndoManager()
            }
        }
    }
}
```
