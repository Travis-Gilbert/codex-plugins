# Navigation Patterns for SwiftUI

## NavigationStack with Path Binding

```swift
struct RootView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Product.self) { product in
                    ProductDetailView(product: product)
                }
                .navigationDestination(for: Category.self) { category in
                    CategoryView(category: category)
                }
                .navigationDestination(for: UserProfile.self) { profile in
                    ProfileView(profile: profile)
                }
        }
    }
}
```

---

## Type-Safe Route Enum

Define all navigation destinations as a single enum for compile-time safety:

```swift
enum Route: Hashable {
    case productDetail(Product)
    case category(Category)
    case userProfile(UserProfile)
    case settings
    case search(query: String)
    case checkout(cart: Cart)

    // For routes with non-Hashable payloads, use IDs
    case orderDetail(orderID: UUID)
}
```

### Using Route with navigationDestination

```swift
struct AppView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView()
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .productDetail(let product):
                        ProductDetailView(product: product)
                    case .category(let category):
                        CategoryView(category: category)
                    case .userProfile(let profile):
                        ProfileView(profile: profile)
                    case .settings:
                        SettingsView()
                    case .search(let query):
                        SearchResultsView(query: query)
                    case .checkout(let cart):
                        CheckoutView(cart: cart)
                    case .orderDetail(let id):
                        OrderDetailView(orderID: id)
                    }
                }
        }
    }
}

// Navigate by appending a Route
Button("View Product") {
    path.append(Route.productDetail(product))
}
```

---

## Router as @Observable Class

Centralize navigation state for programmatic control:

```swift
@Observable
class Router {
    var path = NavigationPath()

    // Sheet presentation
    var presentedSheet: Sheet?

    // Full-screen cover
    var presentedFullScreen: FullScreenDestination?

    // Alert
    var alertItem: AlertItem?

    enum Sheet: Identifiable {
        case addItem
        case editProfile
        case filterOptions(FilterState)

        var id: String { String(describing: self) }
    }

    enum FullScreenDestination: Identifiable {
        case onboarding
        case mediaViewer(URL)
        case camera

        var id: String { String(describing: self) }
    }

    // MARK: - Navigation Actions

    func navigate(to route: Route) {
        path.append(route)
    }

    func popToRoot() {
        path = NavigationPath()
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func pop(count: Int) {
        let removeCount = min(count, path.count)
        path.removeLast(removeCount)
    }

    func presentSheet(_ sheet: Sheet) {
        presentedSheet = sheet
    }

    func dismissSheet() {
        presentedSheet = nil
    }

    func presentFullScreen(_ destination: FullScreenDestination) {
        presentedFullScreen = destination
    }
}
```

### Wiring the Router

```swift
@main
struct MyApp: App {
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $router.path) {
                HomeView()
                    .navigationDestination(for: Route.self) { route in
                        destinationView(for: route)
                    }
            }
            .sheet(item: $router.presentedSheet) { sheet in
                sheetView(for: sheet)
            }
            .fullScreenCover(item: $router.presentedFullScreen) { dest in
                fullScreenView(for: dest)
            }
            .environment(router)
        }
    }

    @ViewBuilder
    func destinationView(for route: Route) -> some View {
        switch route {
        case .productDetail(let product): ProductDetailView(product: product)
        case .settings: SettingsView()
        // ... etc
        }
    }
}

// Any child view can navigate
struct ProductRow: View {
    @Environment(Router.self) private var router
    let product: Product

    var body: some View {
        Button(product.name) {
            router.navigate(to: .productDetail(product))
        }
    }
}
```

---

## Sheet and FullScreenCover Presentation

```swift
struct LibraryView: View {
    @State private var selectedBook: Book?
    @State private var showAddBook = false

    var body: some View {
        List(books) { book in
            BookRow(book: book)
                .onTapGesture { selectedBook = book }
        }
        .toolbar {
            Button("Add", systemImage: "plus") {
                showAddBook = true
            }
        }
        // Item-based sheet
        .sheet(item: $selectedBook) { book in
            BookDetailSheet(book: book)
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
        }
        // Bool-based sheet
        .sheet(isPresented: $showAddBook) {
            AddBookView()
                .interactiveDismissDisabled()  // Prevent swipe dismiss
        }
    }
}

// Nested navigation inside a sheet
struct AddBookView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            BookForm()
                .navigationTitle("New Book")
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel") { dismiss() }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Save") {
                            saveBook()
                            dismiss()
                        }
                    }
                }
        }
    }
}
```

---

## Deep Linking

```swift
@Observable
class Router {
    var path = NavigationPath()
    var selectedTab: AppTab = .home

    func handle(url: URL) {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
              let host = components.host else { return }

        // Reset to root first
        path = NavigationPath()

        switch host {
        case "product":
            if let id = components.queryItems?.first(where: { $0.name == "id" })?.value {
                selectedTab = .shop
                Task {
                    if let product = await ProductService.fetch(id: id) {
                        path.append(Route.productDetail(product))
                    }
                }
            }
        case "profile":
            selectedTab = .profile
        case "settings":
            selectedTab = .profile
            path.append(Route.settings)
        default:
            break
        }
    }
}

// Wire to App
@main
struct MyApp: App {
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            AppTabView()
                .environment(router)
                .onOpenURL { url in
                    router.handle(url: url)
                }
        }
    }
}

// Also handle Universal Links and NSUserActivity
.onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
    if let url = activity.webpageURL {
        router.handle(url: url)
    }
}
```

---

## Tab-Based Navigation with NavigationStack Per Tab

```swift
enum AppTab: String, CaseIterable, Identifiable {
    case home, search, favorites, profile
    var id: Self { self }

    var title: String {
        rawValue.capitalized
    }

    var icon: String {
        switch self {
        case .home: "house"
        case .search: "magnifyingglass"
        case .favorites: "heart"
        case .profile: "person"
        }
    }
}

struct AppTabView: View {
    @Environment(Router.self) private var router

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {
            Tab(AppTab.home.title, systemImage: AppTab.home.icon, value: .home) {
                NavigationStack(path: $router.path) {
                    HomeView()
                        .navigationDestination(for: Route.self) { route in
                            destinationView(for: route)
                        }
                }
            }

            Tab(AppTab.search.title, systemImage: AppTab.search.icon, value: .search) {
                NavigationStack {
                    SearchView()
                        .navigationDestination(for: Route.self) { route in
                            destinationView(for: route)
                        }
                }
            }

            Tab(AppTab.favorites.title, systemImage: AppTab.favorites.icon, value: .favorites) {
                NavigationStack {
                    FavoritesView()
                }
            }

            Tab(AppTab.profile.title, systemImage: AppTab.profile.icon, value: .profile) {
                NavigationStack {
                    ProfileView()
                }
            }
        }
    }
}
```

### Per-Tab Navigation Paths

For independent back stacks per tab:

```swift
@Observable
class TabRouter {
    var selectedTab: AppTab = .home
    var paths: [AppTab: NavigationPath] = [
        .home: NavigationPath(),
        .search: NavigationPath(),
        .favorites: NavigationPath(),
        .profile: NavigationPath(),
    ]

    func navigate(to route: Route, in tab: AppTab? = nil) {
        let targetTab = tab ?? selectedTab
        paths[targetTab, default: NavigationPath()].append(route)
        selectedTab = targetTab
    }

    func popToRoot(tab: AppTab? = nil) {
        let targetTab = tab ?? selectedTab
        paths[targetTab] = NavigationPath()
    }

    func binding(for tab: AppTab) -> Binding<NavigationPath> {
        Binding(
            get: { self.paths[tab, default: NavigationPath()] },
            set: { self.paths[tab] = $0 }
        )
    }
}
```

---

## Pop to Root

```swift
// Method 1: Reset NavigationPath
func popToRoot() {
    path = NavigationPath()
}

// Method 2: Remove specific count
func popLast(_ count: Int = 1) {
    let removeCount = min(count, path.count)
    path.removeLast(removeCount)
}

// Method 3: Double-tap tab to pop to root
TabView(selection: $selectedTab) {
    // ...
}
.onChange(of: selectedTab) { oldTab, newTab in
    if oldTab == newTab {
        // Tab was tapped again — pop to root
        router.popToRoot(tab: newTab)
    }
}
```

---

## Coordinator Pattern

For complex multi-step flows (onboarding, checkout):

```swift
@Observable
class CheckoutCoordinator {
    enum Step: Hashable {
        case cart
        case shipping
        case payment
        case review
        case confirmation(orderID: UUID)
    }

    var path = NavigationPath()
    var currentStep: Step = .cart
    private var cart: Cart
    private var shippingInfo: ShippingInfo?
    private var paymentMethod: PaymentMethod?

    init(cart: Cart) {
        self.cart = cart
    }

    func proceedToShipping() {
        let step = Step.shipping
        path.append(step)
        currentStep = step
    }

    func proceedToPayment(shipping: ShippingInfo) {
        self.shippingInfo = shipping
        let step = Step.payment
        path.append(step)
        currentStep = step
    }

    func proceedToReview(payment: PaymentMethod) {
        self.paymentMethod = payment
        let step = Step.review
        path.append(step)
        currentStep = step
    }

    func placeOrder() async throws {
        guard let shipping = shippingInfo, let payment = paymentMethod else { return }
        let order = try await OrderService.place(cart: cart, shipping: shipping, payment: payment)
        path = NavigationPath()
        path.append(Step.confirmation(orderID: order.id))
    }

    func cancel() {
        path = NavigationPath()
    }
}

struct CheckoutFlow: View {
    @State private var coordinator: CheckoutCoordinator

    init(cart: Cart) {
        _coordinator = State(initialValue: CheckoutCoordinator(cart: cart))
    }

    var body: some View {
        NavigationStack(path: $coordinator.path) {
            CartReviewView(coordinator: coordinator)
                .navigationDestination(for: CheckoutCoordinator.Step.self) { step in
                    switch step {
                    case .cart:
                        CartReviewView(coordinator: coordinator)
                    case .shipping:
                        ShippingFormView(coordinator: coordinator)
                    case .payment:
                        PaymentFormView(coordinator: coordinator)
                    case .review:
                        OrderReviewView(coordinator: coordinator)
                    case .confirmation(let orderID):
                        OrderConfirmationView(orderID: orderID)
                    }
                }
        }
    }
}
```

---

## Navigation State Persistence

Save and restore navigation state across app launches:

```swift
@Observable
class Router {
    var path = NavigationPath()

    private static let pathKey = "savedNavigationPath"

    func save() {
        guard let representation = path.codable else { return }
        if let data = try? JSONEncoder().encode(representation) {
            UserDefaults.standard.set(data, forKey: Self.pathKey)
        }
    }

    func restore() {
        guard let data = UserDefaults.standard.data(forKey: Self.pathKey),
              let representation = try? JSONDecoder().decode(
                  NavigationPath.CodableRepresentation.self, from: data
              ) else { return }
        path = NavigationPath(representation)
    }
}
```

Note: All types in the `NavigationPath` must conform to `Codable` for persistence to work. `NavigationPath.codable` returns `nil` if any element is not `Codable`.
