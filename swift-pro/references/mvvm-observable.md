# MVVM Architecture with @Observable

## Why @Observable, Not ObservableObject

| Concern | `ObservableObject` | `@Observable` |
|---------|-------------------|---------------|
| Re-render scope | Any `@Published` change triggers ALL observing views | Only views reading the changed property re-render |
| Boilerplate | `@Published` on every property | None — all properties tracked automatically |
| View ownership | `@StateObject` vs `@ObservedObject` confusion | Always `@State` for ownership |
| Binding | `$viewModel.property` works directly | Requires `@Bindable` wrapper |
| Performance | Object-level invalidation | Property-level invalidation |
| Combine dependency | Requires `import Combine` | Uses `import Observation` |

The performance difference is significant. With `ObservableObject`, changing `isLoading` re-renders every view observing the object, even if that view only reads `title`. With `@Observable`, only views that actually read `isLoading` re-render.

---

## ViewModel as @Observable Class

```swift
import Observation
import SwiftUI

@Observable
class TaskListViewModel {
    // MARK: - State
    var tasks: [TaskItem] = []
    var isLoading = false
    var error: AppError?
    var searchText = ""
    var selectedFilter: TaskFilter = .all

    // Computed — automatically tracked based on dependencies
    var filteredTasks: [TaskItem] {
        let filtered = switch selectedFilter {
        case .all: tasks
        case .pending: tasks.filter { !$0.isCompleted }
        case .completed: tasks.filter { $0.isCompleted }
        }
        if searchText.isEmpty {
            return filtered
        }
        return filtered.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }

    var pendingCount: Int {
        tasks.filter { !$0.isCompleted }.count
    }

    // MARK: - Dependencies
    private let repository: TaskRepository
    private let analytics: AnalyticsService

    init(repository: TaskRepository, analytics: AnalyticsService = .shared) {
        self.repository = repository
        self.analytics = analytics
    }

    // MARK: - Actions
    func loadTasks() async {
        isLoading = true
        error = nil
        do {
            tasks = try await repository.fetchAll()
            analytics.track(.tasksLoaded(count: tasks.count))
        } catch {
            self.error = AppError(error)
        }
        isLoading = false
    }

    func addTask(title: String) async {
        let task = TaskItem(title: title)
        tasks.append(task)  // Optimistic update
        do {
            try await repository.save(task)
        } catch {
            tasks.removeAll { $0.id == task.id }  // Rollback
            self.error = AppError(error)
        }
    }

    func toggleCompletion(_ task: TaskItem) async {
        guard let index = tasks.firstIndex(where: { $0.id == task.id }) else { return }
        tasks[index].isCompleted.toggle()  // Optimistic
        do {
            try await repository.update(tasks[index])
        } catch {
            tasks[index].isCompleted.toggle()  // Rollback
            self.error = AppError(error)
        }
    }

    func deleteTask(_ task: TaskItem) async {
        let backup = tasks
        tasks.removeAll { $0.id == task.id }
        do {
            try await repository.delete(task)
        } catch {
            tasks = backup
            self.error = AppError(error)
        }
    }
}
```

---

## View Using @State (Not @StateObject)

```swift
struct TaskListView: View {
    // @State owns the ViewModel — replaces @StateObject
    @State private var viewModel: TaskListViewModel

    init(repository: TaskRepository = .live) {
        _viewModel = State(initialValue: TaskListViewModel(repository: repository))
    }

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading && viewModel.tasks.isEmpty {
                    ProgressView("Loading tasks...")
                } else if viewModel.tasks.isEmpty {
                    ContentUnavailableView(
                        "No Tasks",
                        systemImage: "checklist",
                        description: Text("Add a task to get started")
                    )
                } else {
                    taskList
                }
            }
            .navigationTitle("Tasks")
            .searchable(text: $viewModel.searchText)  // Needs @Bindable (see below)
            .toolbar {
                filterPicker
                addButton
            }
            .task {
                await viewModel.loadTasks()
            }
            .alert(item: $viewModel.error) { error in  // Needs @Bindable
                Alert(title: Text("Error"), message: Text(error.message))
            }
        }
    }

    // Note: to use $viewModel.searchText, you need @Bindable
    // Option 1: Declare @Bindable inside body
    // Option 2: Use a wrapper (see below)
}
```

---

## @Bindable for Bindings

```swift
struct TaskListView: View {
    @State private var viewModel = TaskListViewModel(repository: .live)

    var body: some View {
        // Create @Bindable inside body to get $ syntax
        @Bindable var viewModel = viewModel

        NavigationStack {
            List(viewModel.filteredTasks) { task in
                TaskRow(task: task) {
                    Task { await viewModel.toggleCompletion(task) }
                }
            }
            .searchable(text: $viewModel.searchText)
        }
    }
}

// When passing ViewModel to a child view
struct TaskFilterSheet: View {
    @Bindable var viewModel: TaskListViewModel

    var body: some View {
        Picker("Filter", selection: $viewModel.selectedFilter) {
            ForEach(TaskFilter.allCases) { filter in
                Text(filter.displayName).tag(filter)
            }
        }
    }
}
```

---

## Separation of Concerns

### Layer Architecture

```
┌─────────────────────────────────────┐
│  View Layer                         │
│  - SwiftUI Views                    │
│  - @State owns ViewModel            │
│  - Declarative UI only              │
├─────────────────────────────────────┤
│  ViewModel Layer                    │
│  - @Observable classes              │
│  - UI state + actions               │
│  - Transforms domain → view state   │
│  - No UIKit/SwiftUI imports         │
├─────────────────────────────────────┤
│  Service/Repository Layer           │
│  - Protocols for abstraction        │
│  - Network, persistence, etc.       │
│  - Pure business logic              │
├─────────────────────────────────────┤
│  Model Layer                        │
│  - Domain types (structs/enums)     │
│  - @Model for SwiftData entities    │
│  - Codable DTOs                     │
└─────────────────────────────────────┘
```

### ViewModel Rules

1. ViewModels should NOT import SwiftUI (import Observation and Foundation only)
2. ViewModels expose simple types the view can bind to, not complex domain objects
3. ViewModels contain no View code, colors, fonts, or layout logic
4. One ViewModel per screen (not per component)
5. Child components receive data via plain properties, not ViewModels

```swift
// GOOD: ViewModel contains state and logic, no UI
import Observation
import Foundation

@Observable
class OrderViewModel {
    var items: [OrderItem] = []
    var total: Decimal { items.reduce(0) { $0 + $1.subtotal } }
    var canCheckout: Bool { !items.isEmpty && total > 0 }

    private let orderService: OrderService

    init(orderService: OrderService) {
        self.orderService = orderService
    }

    func checkout() async throws -> Order {
        try await orderService.placeOrder(items: items)
    }
}

// BAD: ViewModel contains UI concerns
@Observable
class BadViewModel {
    var titleColor: Color = .blue  // UI concern
    var font: Font = .title        // UI concern
}
```

---

## Dependency Injection

### Via Init (Preferred)

```swift
@Observable
class ProfileViewModel {
    private let userService: UserServiceProtocol
    private let imageLoader: ImageLoaderProtocol

    init(
        userService: UserServiceProtocol = UserService(),
        imageLoader: ImageLoaderProtocol = ImageLoader()
    ) {
        self.userService = userService
        self.imageLoader = imageLoader
    }
}

// In view
struct ProfileView: View {
    @State private var viewModel: ProfileViewModel

    init(userService: UserServiceProtocol = UserService()) {
        _viewModel = State(initialValue: ProfileViewModel(userService: userService))
    }
}
```

### Via @Environment

```swift
// Define environment-injectable services
@Observable
class AuthService {
    var currentUser: User?
    func signIn(email: String, password: String) async throws { /* ... */ }
    func signOut() { currentUser = nil }
}

// Register in app root
@main
struct MyApp: App {
    @State private var authService = AuthService()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(authService)
        }
    }
}

// ViewModel receives from view
@Observable
class SettingsViewModel {
    private let auth: AuthService

    init(auth: AuthService) {
        self.auth = auth
    }
}

struct SettingsView: View {
    @Environment(AuthService.self) private var auth
    @State private var viewModel: SettingsViewModel?

    var body: some View {
        Group {
            if let viewModel {
                SettingsContent(viewModel: viewModel)
            }
        }
        .onAppear {
            viewModel = SettingsViewModel(auth: auth)
        }
    }
}
```

---

## Testing ViewModels

```swift
import Testing

@Suite("TaskListViewModel Tests")
struct TaskListViewModelTests {
    let mockRepository = MockTaskRepository()

    @Test("loads tasks on initial fetch")
    func loadTasks() async throws {
        let expectedTasks = [TaskItem(title: "Test Task")]
        mockRepository.stubbedTasks = expectedTasks

        let viewModel = TaskListViewModel(repository: mockRepository)
        await viewModel.loadTasks()

        #expect(viewModel.tasks == expectedTasks)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.error == nil)
    }

    @Test("handles fetch error gracefully")
    func loadTasksError() async {
        mockRepository.shouldThrow = true

        let viewModel = TaskListViewModel(repository: mockRepository)
        await viewModel.loadTasks()

        #expect(viewModel.tasks.isEmpty)
        #expect(viewModel.error != nil)
        #expect(viewModel.isLoading == false)
    }

    @Test("filters tasks by search text")
    func filterBySearch() async throws {
        let viewModel = TaskListViewModel(repository: mockRepository)
        viewModel.tasks = [
            TaskItem(title: "Buy groceries"),
            TaskItem(title: "Call dentist"),
            TaskItem(title: "Buy birthday gift"),
        ]

        viewModel.searchText = "Buy"
        #expect(viewModel.filteredTasks.count == 2)
    }

    @Test("optimistic update rolls back on error")
    func rollbackOnError() async {
        mockRepository.shouldThrow = true
        let task = TaskItem(title: "Test")

        let viewModel = TaskListViewModel(repository: mockRepository)
        viewModel.tasks = [task]

        await viewModel.toggleCompletion(task)

        #expect(viewModel.tasks.first?.isCompleted == false)
    }
}

// Mock
class MockTaskRepository: TaskRepository {
    var stubbedTasks: [TaskItem] = []
    var shouldThrow = false

    func fetchAll() async throws -> [TaskItem] {
        if shouldThrow { throw TestError.mock }
        return stubbedTasks
    }
    func save(_ task: TaskItem) async throws {
        if shouldThrow { throw TestError.mock }
    }
    func update(_ task: TaskItem) async throws {
        if shouldThrow { throw TestError.mock }
    }
    func delete(_ task: TaskItem) async throws {
        if shouldThrow { throw TestError.mock }
    }
}
```

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Using `@StateObject` with `@Observable` | `@StateObject` is for `ObservableObject` only | Use `@State` |
| Using `@ObservedObject` with `@Observable` | Triggers whole-object observation | Pass as plain property |
| Using `@EnvironmentObject` with `@Observable` | Wrong observation system | Use `@Environment(Type.self)` |
| ViewModel imports SwiftUI | Tight coupling, harder to test | Import only `Observation` + `Foundation` |
| Sharing ViewModel between screens | Coupling, unexpected mutations | Each screen owns its ViewModel |
| Forgetting `@Bindable` for bindings | Cannot use `$` syntax | Add `@Bindable var vm = viewModel` in body |
| Making ViewModel a struct | `@Observable` requires class | Use `class`, not `struct` |
| Using `@Observable` on an actor | Macro not supported on actors | Use `@Observable class` + `@MainActor` |
| Accessing ViewModel from background | Data races with UI state | Mark ViewModel `@MainActor` |
| Giant ViewModel (500+ lines) | Hard to test and reason about | Extract sub-ViewModels or services |
