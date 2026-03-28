# SwiftData Stack Template

## ModelContainer Configuration

```swift
import SwiftData

enum DataStack {
    /// All model types registered with the container.
    static let models: [any PersistentModel.Type] = [
        Project.self,
        Task.self,
        Tag.self,
    ]

    /// Production container with persistent storage.
    static func makeContainer() throws -> ModelContainer {
        let schema = Schema(models)
        let config = ModelConfiguration(
            "AppDatabase",
            schema: schema,
            isStoredInMemoryOnly: false,
            allowsSave: true
        )
        return try ModelContainer(for: schema, configurations: [config])
    }

    /// In-memory container for previews and tests.
    static func makePreviewContainer() throws -> ModelContainer {
        let schema = Schema(models)
        let config = ModelConfiguration(
            schema: schema,
            isStoredInMemoryOnly: true
        )
        let container = try ModelContainer(for: schema, configurations: [config])
        // Seed sample data
        let context = container.mainContext
        SampleData.seed(into: context)
        return container
    }

    /// Container with CloudKit sync enabled.
    static func makeCloudContainer() throws -> ModelContainer {
        let schema = Schema(models)
        let config = ModelConfiguration(
            "AppDatabase",
            schema: schema,
            isStoredInMemoryOnly: false,
            allowsSave: true,
            cloudKitDatabase: .automatic
        )
        return try ModelContainer(for: schema, configurations: [config])
    }
}
```

## Sample @Model Classes with Relationships

```swift
import Foundation
import SwiftData

@Model
final class Project {
    var title: String
    var summary: String
    var createdAt: Date
    var updatedAt: Date
    var isArchived: Bool

    // One-to-many: a project has many tasks
    @Relationship(deleteRule: .cascade, inverse: \Task.project)
    var tasks: [Task]

    // Many-to-many: a project can have many tags
    @Relationship(inverse: \Tag.projects)
    var tags: [Tag]

    #Unique([\.title])

    init(title: String, summary: String = "") {
        self.title = title
        self.summary = summary
        self.createdAt = .now
        self.updatedAt = .now
        self.isArchived = false
        self.tasks = []
        self.tags = []
    }
}

@Model
final class Task {
    var title: String
    var note: String
    var isComplete: Bool
    var priority: Priority
    var dueDate: Date?
    var createdAt: Date

    var project: Project?

    @Transient
    var isOverdue: Bool {
        guard let due = dueDate, !isComplete else { return false }
        return due < .now
    }

    enum Priority: Int, Codable, CaseIterable {
        case low = 0
        case medium = 1
        case high = 2
        case urgent = 3
    }

    init(title: String, priority: Priority = .medium, project: Project? = nil) {
        self.title = title
        self.note = ""
        self.isComplete = false
        self.priority = priority
        self.dueDate = nil
        self.createdAt = .now
        self.project = project
    }
}

@Model
final class Tag {
    #Unique([\.name])

    var name: String
    var color: String

    var projects: [Project]

    init(name: String, color: String = "#007AFF") {
        self.name = name
        self.color = color
        self.projects = []
    }
}
```

## @Query Usage in Views

```swift
import SwiftUI
import SwiftData

struct ProjectListView: View {
    // Basic query with sort
    @Query(sort: \Project.updatedAt, order: .reverse)
    private var projects: [Project]

    // Filtered query
    @Query(
        filter: #Predicate<Task> { $0.isComplete == false },
        sort: \Task.createdAt,
        order: .reverse
    )
    private var pendingTasks: [Task]

    // Query with fetch limit
    @Query(
        sort: \Task.priority,
        order: .reverse,
        animation: .default
    )
    private var allTasks: [Task]

    @Environment(\.modelContext) private var context

    var body: some View {
        List {
            ForEach(projects) { project in
                ProjectRow(project: project)
            }
            .onDelete(perform: deleteProjects)
        }
    }

    private func deleteProjects(at offsets: IndexSet) {
        for index in offsets {
            context.delete(projects[index])
        }
    }
}

// Dynamic filtering with init parameter
struct FilteredTaskList: View {
    @Query private var tasks: [Task]

    init(showCompleted: Bool) {
        let predicate: Predicate<Task>
        if showCompleted {
            predicate = #Predicate { _ in true }
        } else {
            predicate = #Predicate { $0.isComplete == false }
        }
        _tasks = Query(filter: predicate, sort: \Task.createdAt)
    }

    var body: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
    }
}
```

## CRUD Operations with ModelContext

```swift
extension ProjectListView {
    func createProject(title: String) {
        let project = Project(title: title)
        context.insert(project)
        // Autosave handles persistence; explicit save if needed:
        // try? context.save()
    }

    func addTask(to project: Project, title: String) {
        let task = Task(title: title, project: project)
        context.insert(task)
    }

    func toggleComplete(_ task: Task) {
        task.isComplete.toggle()
    }

    func fetchProjects(matching query: String) throws -> [Project] {
        let predicate = #Predicate<Project> {
            $0.title.localizedStandardContains(query)
        }
        let descriptor = FetchDescriptor(predicate: predicate, sortBy: [SortDescriptor(\.updatedAt, order: .reverse)])
        return try context.fetch(descriptor)
    }
}
```

## Migration Plan Structure

```swift
import SwiftData

// Version 1 schema
enum SchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] {
        [ProjectV1.self, TaskV1.self]
    }

    @Model final class ProjectV1 {
        var title: String
        var createdAt: Date
        init(title: String) {
            self.title = title
            self.createdAt = .now
        }
    }

    @Model final class TaskV1 {
        var title: String
        init(title: String) { self.title = title }
    }
}

// Version 2 schema (added summary to Project)
enum SchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] {
        [Project.self, Task.self, Tag.self]
    }
}

// Migration plan
enum AppMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: SchemaV1.self,
        toVersion: SchemaV2.self
    )

    // For complex migrations use .custom:
    // static let migrateV1toV2 = MigrationStage.custom(
    //     fromVersion: SchemaV1.self,
    //     toVersion: SchemaV2.self
    // ) { context in
    //     // Manual data transformation
    //     try context.save()
    // }
}
```
