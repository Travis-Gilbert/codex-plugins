// REFERENCE: @Bindable Property Wrapper
// Creating bindings from @Observable objects in SwiftUI

// ─── @Bindable Overview ──────────────────────────────────────────────
// @Bindable creates Binding<T> accessors for @Observable properties.
// Use when a SwiftUI control needs a $binding to an @Observable property.

import SwiftUI
import Observation

@Observable
final class FormData {
    var username: String = ""
    var email: String = ""
    var agreeToTerms: Bool = false
    var selectedColor: Color = .blue
}

// ─── @Bindable with @State ───────────────────────────────────────────
// When the view owns the @Observable object via @State,
// you can create bindings directly with $:

struct FormView: View {
    @State private var form = FormData()

    var body: some View {
        Form {
            // $form.username creates a Binding<String>
            TextField("Username", text: $form.username)
            TextField("Email", text: $form.email)
            Toggle("Agree", isOn: $form.agreeToTerms)
            ColorPicker("Color", selection: $form.selectedColor)
        }
    }
}

// ─── @Bindable with Passed-In Objects ────────────────────────────────
// When an @Observable object is passed as a parameter (not owned via @State),
// use @Bindable to create bindings:

struct EditProfileView: View {
    @Bindable var profile: FormData  // NOT owned by this view

    var body: some View {
        Form {
            TextField("Username", text: $profile.username)
            TextField("Email", text: $profile.email)
        }
    }
}

// Parent provides it:
// struct ParentView: View {
//     @State private var form = FormData()
//     var body: some View {
//         EditProfileView(profile: form)
//     }
// }

// ─── @Bindable with @Environment ─────────────────────────────────────
// When reading @Observable from @Environment, use @Bindable locally:

struct SettingsView: View {
    @Environment(FormData.self) private var form

    var body: some View {
        // Create a local @Bindable to get $ access
        @Bindable var form = form

        Form {
            TextField("Username", text: $form.username)
            Toggle("Agree", isOn: $form.agreeToTerms)
        }
    }
}

// ─── When to Use @Bindable vs @State ─────────────────────────────────
//
// @State private var model = MyModel()
//   → View OWNS the model (creates and manages its lifecycle)
//   → Already supports $ syntax
//
// @Bindable var model: MyModel
//   → View receives the model from outside
//   → Needs @Bindable to get $ syntax for bindings
//
// @Environment(MyModel.self) var model
//   → View reads from environment
//   → Use local `@Bindable var model = model` for $ access

// ─── Binding to Nested Properties ────────────────────────────────────

@Observable
final class Order {
    var item: Item = Item()
    var quantity: Int = 1
}

@Observable
final class Item {
    var name: String = ""
    var price: Double = 0
}

struct OrderView: View {
    @Bindable var order: Order

    var body: some View {
        Form {
            // Bind to nested @Observable properties
            TextField("Item name", text: $order.item.name)

            // Bind to primitive types
            Stepper("Qty: \(order.quantity)", value: $order.quantity, in: 1...99)
        }
    }
}

// ─── Custom Bindings from @Observable ────────────────────────────────
// Sometimes you need a computed/transformed binding:

struct TemperatureView: View {
    @Bindable var settings: AppSettings

    var body: some View {
        // Create a manual binding with get/set
        let fahrenheitBinding = Binding<Double>(
            get: { settings.temperatureCelsius * 9 / 5 + 32 },
            set: { settings.temperatureCelsius = ($0 - 32) * 5 / 9 }
        )

        Slider(value: fahrenheitBinding, in: 32...212)
    }
}

// ─── Migration from ObservableObject Bindings ────────────────────────
//
// BEFORE:
//   class ViewModel: ObservableObject {
//       @Published var text: String = ""
//   }
//   struct MyView: View {
//       @ObservedObject var vm: ViewModel
//       var body: some View {
//           TextField("", text: $vm.text)
//       }
//   }
//
// AFTER:
//   @Observable final class ViewModel {
//       var text: String = ""
//   }
//   struct MyView: View {
//       @Bindable var vm: ViewModel
//       var body: some View {
//           TextField("", text: $vm.text)
//       }
//   }
