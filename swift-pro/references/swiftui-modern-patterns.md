# Modern SwiftUI Patterns (iOS 17+)

## @Observable vs ObservableObject

### The Old Way (ObservableObject)

```swift
// iOS 13–16: Manual property publishing
class ProfileViewModel: ObservableObject {
    @Published var name: String = ""
    @Published var isLoading: Bool = false
    // Every @Published property triggers observation even if view doesn't use it
}

struct ProfileView: View {
    @StateObject var viewModel = ProfileViewModel()  // Ownership
    // or @ObservedObject for injected
    var body: some View {
        Text(viewModel.name)  // Observes ALL @Published changes
    }
}
```

### The New Way (@Observable)

```swift
// iOS 17+: Automatic, fine-grained tracking
@Observable
class ProfileViewModel {
    var name: String = ""       // No @Published needed
    var isLoading: Bool = false
    // SwiftUI only re-renders when accessed properties change
}

struct ProfileView: View {
    @State var viewModel = ProfileViewModel()  // @State, not @StateObject
    var body: some View {
        Text(viewModel.name)  // Only re-renders when `name` changes
        // Changes to `isLoading` do NOT trigger re-render here
    }
}
```

### Comparison Table

| Feature | `ObservableObject` | `@Observable` |
|---------|-------------------|---------------|
| Import | `Combine` | `Observation` |
| Property wrapper | `@Published` | None (automatic) |
| View ownership | `@StateObject` | `@State` |
| View injection | `@ObservedObject` | Plain property |
| Environment | `@EnvironmentObject` | `@Environment` |
| Observation granularity | Whole object (any @Published) | Per-property (only accessed) |
| Binding creation | `$viewModel.name` | Requires `@Bindable` |
| Minimum target | iOS 13 | iOS 17 |

---

## @Bindable

Creates bindings from `@Observable` objects:

```swift
@Observable
class FormData {
    var username: String = ""
    var email: String = ""
    var agreeToTerms: Bool = false
}

struct FormView: View {
    @State private var form = FormData()

    var body: some View {
        Form {
            // @Bindable enables $ syntax for @Observable
            @Bindable var form = form

            TextField("Username", text: $form.username)
            TextField("Email", text: $form.email)
            Toggle("Agree to terms", isOn: $form.agreeToTerms)
        }
    }
}

// Also works with parameters
struct EditView: View {
    @Bindable var item: Item  // Item is @Observable

    var body: some View {
        TextField("Name", text: $item.name)
    }
}
```

---

## NavigationStack

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationTitle("Items")
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
            .navigationDestination(for: Category.self) { category in
                CategoryView(category: category)
            }
        }
    }

    func popToRoot() {
        path = NavigationPath()
    }
}
```

---

## Typed Throws (Swift 6 / Xcode 16)

```swift
enum ValidationError: Error {
    case tooShort
    case invalidCharacters
    case alreadyTaken
}

// Caller knows exactly which errors to handle
func validateUsername(_ name: String) throws(ValidationError) -> String {
    guard name.count >= 3 else { throw .tooShort }
    guard name.allSatisfy(\.isLetterOrDigit) else { throw .invalidCharacters }
    return name
}

// Exhaustive catch
do {
    let validated = try validateUsername(input)
} catch .tooShort {
    showError("Username must be at least 3 characters")
} catch .invalidCharacters {
    showError("Only letters and digits allowed")
} catch .alreadyTaken {
    showError("This username is taken")
}
// No need for a catch-all — compiler knows these are exhaustive
```

---

## ContentUnavailableView

```swift
struct SearchResultsView: View {
    let results: [Item]
    let searchText: String

    var body: some View {
        if results.isEmpty {
            ContentUnavailableView.search(text: searchText)
        } else {
            List(results) { item in
                ItemRow(item: item)
            }
        }
    }
}

// Custom unavailable view
struct EmptyLibraryView: View {
    var body: some View {
        ContentUnavailableView {
            Label("No Books", systemImage: "books.vertical")
        } description: {
            Text("Your library is empty. Add books to get started.")
        } actions: {
            Button("Browse Store") {
                // action
            }
            .buttonStyle(.borderedProminent)
        }
    }
}
```

---

## ViewThatFits

Automatically picks the first child that fits the available space:

```swift
struct AdaptiveHeader: View {
    let title: String
    let subtitle: String

    var body: some View {
        ViewThatFits(in: .horizontal) {
            // First choice: full horizontal layout
            HStack {
                Text(title).font(.title)
                Spacer()
                Text(subtitle).font(.subheadline)
            }

            // Fallback: stacked layout
            VStack(alignment: .leading) {
                Text(title).font(.title2)
                Text(subtitle).font(.caption)
            }
        }
    }
}
```

---

## Sensory Feedback

```swift
struct InteractiveView: View {
    @State private var isLiked = false

    var body: some View {
        Button {
            isLiked.toggle()
        } label: {
            Image(systemName: isLiked ? "heart.fill" : "heart")
                .foregroundStyle(isLiked ? .red : .secondary)
        }
        .sensoryFeedback(.impact(weight: .medium), trigger: isLiked)
    }
}

// Available feedback types:
// .success, .warning, .error
// .selection
// .impact(weight: .light/.medium/.heavy, intensity: 0...1)
// .increase, .decrease
// .start, .stop
// .alignment, .levelChange, .pathComplete
```

---

## .onChange(of:) New Syntax

```swift
struct SearchView: View {
    @State private var searchText = ""
    @State private var results: [Item] = []

    var body: some View {
        List(results) { item in
            ItemRow(item: item)
        }
        .searchable(text: $searchText)
        // iOS 17+ syntax: two parameters (oldValue, newValue)
        .onChange(of: searchText) { oldValue, newValue in
            guard newValue != oldValue else { return }
            performSearch(newValue)
        }
        // For initial value, use .onChange with `initial: true`
        .onChange(of: searchText, initial: true) { oldValue, newValue in
            performSearch(newValue)
        }
    }
}
```

---

## .task Modifier

```swift
struct ProfileView: View {
    @State private var profile: Profile?
    @State private var error: Error?

    let userID: String

    var body: some View {
        Group {
            if let profile {
                ProfileContent(profile: profile)
            } else if let error {
                ErrorView(error: error)
            } else {
                ProgressView()
            }
        }
        // Cancelled automatically when view disappears or userID changes
        .task(id: userID) {
            do {
                profile = try await ProfileService.fetch(id: userID)
            } catch {
                if !Task.isCancelled {
                    self.error = error
                }
            }
        }
    }
}

// Long-running observation
struct LiveUpdatesView: View {
    @State private var messages: [Message] = []

    var body: some View {
        MessageList(messages: messages)
            .task {
                // Automatically cancelled when view disappears
                for await message in MessageStream.live() {
                    messages.append(message)
                }
            }
    }
}
```

---

## @Environment for Custom Values

```swift
// Define the key
struct ThemeKey: EnvironmentKey {
    static let defaultValue = Theme.standard
}

extension EnvironmentValues {
    var theme: Theme {
        get { self[ThemeKey.self] }
        set { self[ThemeKey.self] = newValue }
    }
}

// With @Observable (iOS 17+), inject observable objects via @Environment
@Observable
class AuthService {
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
}

extension EnvironmentValues {
    @Entry var authService: AuthService = AuthService()
}

// Usage
struct RootView: View {
    @State private var auth = AuthService()

    var body: some View {
        ContentView()
            .environment(\.authService, auth)
    }
}

struct ProfileView: View {
    @Environment(\.authService) private var auth

    var body: some View {
        if let user = auth.currentUser {
            Text("Hello, \(user.name)")
        }
    }
}

// Simpler: inject @Observable directly by type
struct AppView: View {
    @State private var settings = AppSettings()

    var body: some View {
        ContentView()
            .environment(settings)  // By type, not key path
    }
}

struct ChildView: View {
    @Environment(AppSettings.self) private var settings
}
```

---

## Sheet and Inspector Patterns

```swift
struct MainView: View {
    @State private var selectedItem: Item?
    @State private var showSettings = false
    @State private var showInspector = false

    var body: some View {
        NavigationStack {
            List(items) { item in
                Button(item.name) {
                    selectedItem = item
                }
            }
            .toolbar {
                Button("Settings", systemImage: "gear") {
                    showSettings = true
                }
                Button("Inspector", systemImage: "sidebar.trailing") {
                    showInspector.toggle()
                }
            }
            // Item-based sheet (iOS 16.4+)
            .sheet(item: $selectedItem) { item in
                ItemDetailSheet(item: item)
                    .presentationDetents([.medium, .large])
                    .presentationDragIndicator(.visible)
                    .presentationCornerRadius(20)
                    .presentationBackgroundInteraction(.enabled(upThrough: .medium))
            }
            // Bool-based sheet
            .sheet(isPresented: $showSettings) {
                SettingsView()
            }
            // Inspector (iOS 17+)
            .inspector(isPresented: $showInspector) {
                InspectorView()
                    .inspectorColumnWidth(min: 200, ideal: 300, max: 400)
            }
        }
    }
}

// Full-screen cover with custom transition (iOS 16.4+)
.fullScreenCover(isPresented: $showOnboarding) {
    OnboardingView()
        .presentationCompactAdaptation(.fullScreenCover)
}
```

---

## ScrollView Enhancements (iOS 17+)

```swift
struct ContentFeed: View {
    @State private var scrollPosition: Item.ID?

    var body: some View {
        ScrollView {
            LazyVStack {
                ForEach(items) { item in
                    ItemCard(item: item)
                }
            }
            .scrollTargetLayout()
        }
        .scrollPosition(id: $scrollPosition)
        .scrollTargetBehavior(.viewAligned)
        .defaultScrollAnchor(.bottom)  // Start at bottom (chat-like)

        Button("Scroll to Top") {
            withAnimation {
                scrollPosition = items.first?.id
            }
        }
    }
}
```

---

## Phased State with PhaseAnimator

```swift
struct PulsingDot: View {
    var body: some View {
        Circle()
            .fill(.blue)
            .frame(width: 20, height: 20)
            .phaseAnimator([false, true]) { content, phase in
                content
                    .scaleEffect(phase ? 1.5 : 1.0)
                    .opacity(phase ? 0.5 : 1.0)
            } animation: { phase in
                .easeInOut(duration: 0.8)
            }
    }
}
```

---

## SwiftUI Previews (Modern Syntax)

```swift
// Lightweight preview syntax (Xcode 15+)
#Preview {
    ProfileView()
        .environment(AuthService())
}

#Preview("Dark Mode") {
    ProfileView()
        .preferredColorScheme(.dark)
}

#Preview(traits: .landscapeLeft) {
    LandscapeOnlyView()
}
```
