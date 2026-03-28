// REFERENCE: @Observable Macro (Observation framework)
// Property tracking, SwiftUI integration, migration from ObservableObject

// ─── @Observable Declaration ─────────────────────────────────────────
// @Observable replaces ObservableObject + @Published.
// The macro synthesizes property tracking automatically.

import Observation

@Observable
final class UserProfile {
    var name: String = ""
    var email: String = ""
    var avatarURL: URL?
    var isVerified: Bool = false

    // Computed properties are tracked if they depend on tracked stored properties
    var displayName: String {
        isVerified ? "\(name) ✓" : name
    }

    // Use @ObservationIgnored to opt out a property from tracking
    @ObservationIgnored
    var internalCache: [String: Any] = [:]
}

// ─── SwiftUI Integration ─────────────────────────────────────────────
// SwiftUI automatically observes @Observable objects used in body.
// No need for @ObservedObject, @StateObject, or objectWillChange.

struct ProfileView: View {
    // For owned state, use @State
    @State private var profile = UserProfile()

    var body: some View {
        VStack {
            TextField("Name", text: $profile.name)
            TextField("Email", text: $profile.email)
            Text(profile.displayName)
        }
    }
}

// For shared/injected state, use @Environment
struct ChildView: View {
    @Environment(UserProfile.self) private var profile

    var body: some View {
        Text(profile.name)
    }
}

// Providing via environment:
// ProfileView()
//     .environment(profile)

// ─── Property Tracking ──────────────────────────────────────────────
// The Observation framework tracks which properties a view actually reads.
// Views only re-render when properties they USE change.

@Observable
final class AppState {
    var userName: String = ""       // Only views reading userName re-render
    var itemCount: Int = 0          // Only views reading itemCount re-render
    var settings: Settings = .init() // Only views reading settings re-render
}

// If a view only reads `userName`, changing `itemCount` does NOT trigger a re-render.
// This is a major improvement over ObservableObject where ANY @Published change
// triggered ALL observers.

// ─── withObservationTracking ─────────────────────────────────────────
// Manually track property access outside SwiftUI.
// The onChange callback fires ONCE when any tracked property changes.

func observeProfile(_ profile: UserProfile) {
    withObservationTracking {
        // Access properties you want to track
        _ = profile.name
        _ = profile.email
    } onChange: {
        // Called once when name OR email changes
        // Must re-register to keep observing
        print("Profile changed")
        observeProfile(profile)  // Re-register
    }
}

// ─── @ObservationIgnored ─────────────────────────────────────────────
// Exclude properties from observation tracking.

@Observable
final class DataManager {
    var items: [Item] = []              // Tracked
    var isLoading: Bool = false         // Tracked

    @ObservationIgnored
    var fetchTask: Task<Void, Never>?   // Not tracked — internal state

    @ObservationIgnored
    var logger = Logger()               // Not tracked — utility
}

// ─── Migration from ObservableObject ─────────────────────────────────
//
// BEFORE (ObservableObject):
//   class ViewModel: ObservableObject {
//       @Published var items: [Item] = []
//       @Published var isLoading = false
//   }
//   struct MyView: View {
//       @StateObject private var vm = ViewModel()
//       // or @ObservedObject var vm: ViewModel
//   }
//
// AFTER (@Observable):
//   @Observable
//   final class ViewModel {
//       var items: [Item] = []
//       var isLoading = false
//   }
//   struct MyView: View {
//       @State private var vm = ViewModel()
//       // or pass via .environment()
//   }
//
// Key changes:
//   ObservableObject → @Observable
//   @Published      → (remove, all properties are tracked)
//   @StateObject    → @State
//   @ObservedObject → @Environment or parameter
//   @EnvironmentObject → @Environment

// ─── Nested Observable Objects ───────────────────────────────────────
// @Observable objects can contain other @Observable objects.
// SwiftUI tracks through the chain.

@Observable
final class AuthState {
    var isLoggedIn: Bool = false
    var currentUser: UserProfile?  // Also @Observable — changes propagate
}

// A view reading `authState.currentUser?.name` re-renders when name changes.

// ─── Thread Safety Note ──────────────────────────────────────────────
// @Observable does NOT provide thread safety.
// Mutate from the same isolation context (typically @MainActor for UI state).
// Combine @Observable with @MainActor for view models:

@MainActor
@Observable
final class SafeViewModel {
    var data: [String] = []
    // All mutations happen on MainActor — safe for SwiftUI
}
