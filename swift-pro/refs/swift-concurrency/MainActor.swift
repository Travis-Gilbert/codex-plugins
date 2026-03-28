// REFERENCE: MainActor
// @MainActor declaration, MainActor.run, isolation inheritance, UI thread

// ─── @MainActor Declaration ──────────────────────────────────────────
// @MainActor ensures code runs on the main thread (UI thread).
// Apply to classes, structs, functions, or properties.

// On a class — all properties and methods are main-actor-isolated:
@MainActor
final class ProfileViewModel {
    var name: String = ""
    var isLoading: Bool = false

    func load() async {
        isLoading = true
        defer { isLoading = false }
        name = await fetchName()  // `await` because fetchName may not be on MainActor
    }
}

// On a single function:
@MainActor
func updateUI(with data: Data) {
    label.text = String(data: data, encoding: .utf8)
}

// On a single property:
class DataManager {
    @MainActor var displayText: String = ""
}

// ─── MainActor.run ───────────────────────────────────────────────────
// Hop to the main actor from a non-main context.

func processInBackground() async {
    let result = await heavyComputation()  // Runs on cooperative pool

    await MainActor.run {
        // Now on the main thread — safe to update UI
        viewModel.result = result
        viewModel.isLoading = false
    }
}

// MainActor.run returns a value:
func fetchAndFormat() async -> String {
    let data = await fetchData()
    let formatted = await MainActor.run {
        formatter.string(from: data)  // Formatter might be main-actor-isolated
    }
    return formatted
}

// ─── Isolation Inheritance ───────────────────────────────────────────
// When a @MainActor class creates a Task {}, the task inherits MainActor.

@MainActor
final class SearchViewModel {
    var query: String = ""
    var results: [SearchResult] = []

    func search() {
        Task {
            // This Task inherits @MainActor because SearchViewModel is @MainActor
            let data = try await api.search(query: query)
            results = data  // Safe — still on MainActor
        }
    }
}

// Task.detached does NOT inherit the actor:
@MainActor
final class ExportViewModel {
    func export() {
        Task.detached {
            // NOT on MainActor — good for heavy work
            let pdf = await generatePDF()

            await MainActor.run {
                // Hop back to update UI
                self.showShareSheet(for: pdf)
            }
        }
    }
}

// ─── UI Thread Guarantees ────────────────────────────────────────────
// SwiftUI Views and their body are implicitly @MainActor.
// UIKit/AppKit view controllers are @MainActor.

// SwiftUI — body is already @MainActor:
struct ContentView: View {
    @State private var viewModel = ProfileViewModel()  // @MainActor

    var body: some View {
        Text(viewModel.name)
            .task {
                // .task runs on MainActor for SwiftUI views
                await viewModel.load()
            }
    }
}

// ─── Common Patterns ─────────────────────────────────────────────────

// Pattern 1: ViewModel with async loading
@MainActor
@Observable
final class ItemListViewModel {
    var items: [Item] = []
    var error: String?
    var isLoading = false

    private let service: ItemService

    init(service: ItemService = .shared) {
        self.service = service
    }

    func loadItems() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await service.fetchItems()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// Pattern 2: Nonisolated async helper on a MainActor class
@MainActor
final class SyncManager {
    var lastSyncDate: Date?

    // Heavy work that should NOT block the main thread
    nonisolated func performSync() async throws -> SyncResult {
        // Runs on cooperative thread pool, NOT MainActor
        let data = try await downloadAllData()
        let result = try processSyncData(data)
        return result
    }

    func syncAndUpdate() async {
        do {
            let result = try await performSync()  // Off main thread
            // Back on MainActor automatically (method is isolated)
            lastSyncDate = result.completedAt
        } catch {
            // Handle error on MainActor
        }
    }
}

// Pattern 3: MainActor.assumeIsolated (Swift 5.9+)
// Assert that you are already on the main actor without suspending.
// Use in callbacks from frameworks that guarantee main-thread delivery.

func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
    MainActor.assumeIsolated {
        // We know UIKit delivers this on the main thread
        viewModel.selectItem(at: indexPath.row)
    }
}

// ─── Pitfalls ────────────────────────────────────────────────────────

// WRONG: Blocking the main actor with synchronous heavy work
// @MainActor
// func processLargeFile() {
//     let data = loadHugeFile()     // Blocks UI!
//     let parsed = parseData(data)  // Still blocking!
// }

// RIGHT: Do heavy work off-MainActor
// @MainActor
// func processLargeFile() async {
//     let parsed = await Task.detached {
//         let data = loadHugeFile()
//         return parseData(data)
//     }.value
//     displayResult(parsed)  // Back on MainActor
// }
