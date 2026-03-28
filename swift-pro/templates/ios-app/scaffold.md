# iOS App Scaffold -- SwiftUI + SwiftData + MVVM

## Directory Structure

```
AppName/
  AppNameApp.swift          # @main entry point
  AppState.swift            # @Observable app-wide state
  Router.swift              # NavigationStack routing
  ModelContainer+App.swift  # SwiftData container setup
  Info.plist

  Features/
    Home/
      Views/
        HomeView.swift
      ViewModels/
        HomeViewModel.swift
      Models/
        HomeItem.swift

  Shared/
    Components/             # Reusable SwiftUI views
    Extensions/             # Foundation / SwiftUI extensions
    Services/               # Networking, persistence helpers
    Theme/                  # Colors, fonts, spacing tokens
```

## AppNameApp.swift

```swift
import SwiftUI
import SwiftData

@main
struct AppNameApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(appState)
        }
        .modelContainer(for: AppSchema.models)
    }
}
```

## AppState.swift

```swift
import Foundation

@Observable
final class AppState {
    var isAuthenticated = false
    var selectedTab: Tab = .home
    var errorMessage: String?

    enum Tab: String, CaseIterable {
        case home, search, settings
    }
}
```

## Router.swift

```swift
import SwiftUI

@Observable
final class Router {
    var path = NavigationPath()

    enum Destination: Hashable {
        case detail(id: String)
        case settings
        case profile(userID: String)
    }

    func push(_ destination: Destination) {
        path.append(destination)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

// Usage in a root view:
//
// struct RootView: View {
//     @State private var router = Router()
//
//     var body: some View {
//         NavigationStack(path: $router.path) {
//             HomeView()
//                 .navigationDestination(for: Router.Destination.self) { dest in
//                     switch dest {
//                     case .detail(let id):    DetailView(id: id)
//                     case .settings:          SettingsView()
//                     case .profile(let uid):  ProfileView(userID: uid)
//                     }
//                 }
//         }
//         .environment(router)
//     }
// }
```

## ModelContainer Setup

```swift
import SwiftData

enum AppSchema {
    static let models: [any PersistentModel.Type] = [
        Item.self,
        Tag.self,
    ]

    static var container: ModelContainer {
        let schema = Schema(models)
        let config = ModelConfiguration(
            "AppName",
            schema: schema,
            isStoredInMemoryOnly: false,
            allowsSave: true
        )
        do {
            return try ModelContainer(for: schema, configurations: [config])
        } catch {
            fatalError("Failed to create ModelContainer: \(error)")
        }
    }
}
```

## Sample Feature Module (Home)

```swift
// Features/Home/Views/HomeView.swift
import SwiftUI
import SwiftData

struct HomeView: View {
    @Query(sort: \Item.createdAt, order: .reverse) private var items: [Item]
    @Environment(Router.self) private var router
    @State private var viewModel = HomeViewModel()

    var body: some View {
        List(items) { item in
            ItemRow(item: item)
                .onTapGesture {
                    router.push(.detail(id: item.id))
                }
        }
        .navigationTitle("Home")
        .task { await viewModel.load() }
    }
}

// Features/Home/ViewModels/HomeViewModel.swift
@Observable
final class HomeViewModel {
    var isLoading = false
    var errorMessage: String?

    func load() async {
        isLoading = true
        defer { isLoading = false }
        // fetch data or trigger SwiftData operations
    }
}
```

## Info.plist Essentials

Key entries to configure early:

| Key | Purpose |
|-----|---------|
| `CFBundleDisplayName` | App display name |
| `UILaunchStoryboardName` | Launch screen (or use SwiftUI launch) |
| `UISupportedInterfaceOrientations` | Portrait / landscape |
| `NSAppTransportSecurity` | ATS exceptions if needed |
| `CFBundleURLTypes` | Deep link URL schemes |
| `UIBackgroundModes` | Background fetch, remote notifications |
| `NSCameraUsageDescription` | Privacy strings for Camera |
| `NSPhotoLibraryUsageDescription` | Privacy strings for Photos |

## Conventions

- Use `@Observable` for all view models (not ObservableObject / @Published).
- Use `NavigationStack` with typed destinations (not NavigationView).
- Keep view `body` under 100 lines; extract subviews early.
- Use `@Query` for SwiftData reads; use `ModelContext` for writes.
- Prefer `async/await` over Combine for asynchronous work.
