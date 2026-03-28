// REFERENCE: Observation Tracking Internals
// How @Observable and withObservationTracking work under the hood

// ─── How @Observable Works ───────────────────────────────────────────
// The @Observable macro expands to:
// 1. A stored property `_$observationRegistrar` of type ObservationRegistrar
// 2. Each stored property is rewritten to call registrar access/mutation hooks
// 3. The type conforms to the Observable protocol

// Conceptual expansion of:
//   @Observable final class Counter { var count: Int = 0 }

/*
final class Counter: Observable {
    private let _$observationRegistrar = ObservationRegistrar()

    private var _count: Int = 0

    var count: Int {
        get {
            _$observationRegistrar.access(self, keyPath: \.count)
            return _count
        }
        set {
            _$observationRegistrar.withMutation(of: self, keyPath: \.count) {
                _count = newValue
            }
        }
    }
}
*/

// ─── ObservationRegistrar ────────────────────────────────────────────
// The registrar tracks which properties are accessed during an observation scope
// and notifies observers when those specific properties change.

// Key methods (internal to the framework):
//   access(_:keyPath:)       — Records a property read
//   withMutation(of:keyPath:_:) — Wraps a property write, notifies observers
//   willSet / didSet hooks   — Called around mutations

// ─── withObservationTracking Flow ────────────────────────────────────
// 1. SwiftUI (or your code) calls withObservationTracking
// 2. During the `apply` closure, all property accesses are recorded
// 3. The registrar builds a set of (object, keyPath) pairs
// 4. When ANY of those properties change, `onChange` fires ONCE
// 5. The tracking is consumed — must re-register to keep observing

import Observation

@Observable
final class Settings {
    var theme: String = "light"
    var fontSize: Int = 14
    var showSidebar: Bool = true
}

func demonstrateTracking(settings: Settings) {
    withObservationTracking {
        // These accesses are recorded:
        let _ = settings.theme       // Tracked
        let _ = settings.fontSize    // Tracked
        // settings.showSidebar is NOT accessed, so NOT tracked
    } onChange: {
        // Fires when theme OR fontSize change
        // Does NOT fire when showSidebar changes
        print("Tracked property changed")
    }
}

// ─── SwiftUI's Observation Loop ──────────────────────────────────────
// SwiftUI's rendering engine effectively does:
//
// 1. withObservationTracking {
//        let bodyResult = view.body  // Records all property accesses
//    } onChange: {
//        scheduleViewUpdate()       // Mark view as needing re-render
//    }
//
// 2. When onChange fires, SwiftUI calls body again
//    which re-registers new tracking for the next change.
//
// This means:
// - Only properties READ during body are tracked
// - Conditional branches matter: if a property is behind an `if` that
//   doesn't execute, it won't be tracked
// - Re-tracking happens automatically on each render

// ─── Tracking Granularity ────────────────────────────────────────────

@Observable
final class FormState {
    var firstName: String = ""
    var lastName: String = ""
    var email: String = ""
    var phone: String = ""
}

// View A only reads firstName:
// → Only re-renders when firstName changes

// View B reads firstName + lastName:
// → Re-renders when either changes

// View C reads all four:
// → Re-renders when any of the four change

// This per-property granularity is why @Observable is more efficient
// than ObservableObject, which notified on ANY @Published change.

// ─── Observation with Collections ────────────────────────────────────
// Arrays of @Observable objects: changes to individual items
// are tracked at the property level.

@Observable
final class TodoItem {
    var title: String
    var isDone: Bool = false
    init(title: String) { self.title = title }
}

@Observable
final class TodoList {
    var items: [TodoItem] = []
}

// A view iterating `todoList.items` tracks:
//   - todoList.items (the array itself — inserts/removals)
//   - Each item.title, item.isDone (if accessed during rendering)
// Changing one item's isDone only re-renders that item's row,
// not the entire list.

// ─── Manual Observation Outside SwiftUI ──────────────────────────────
// For non-SwiftUI contexts (UIKit, AppKit, background services),
// use withObservationTracking with a re-registration pattern:

final class UIKitObserver {
    private var isObserving = true

    func startObserving(_ model: Settings) {
        guard isObserving else { return }

        withObservationTracking {
            updateLabel(model.theme)
            updateSlider(model.fontSize)
        } onChange: { [weak self] in
            // Dispatch to main queue for UIKit
            DispatchQueue.main.async {
                self?.startObserving(model)  // Re-register
            }
        }
    }

    func stopObserving() {
        isObserving = false
    }
}
