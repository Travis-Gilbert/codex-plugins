---
description: Scaffold a SwiftUI view + ViewModel
allowed-tools: Read, Write, Glob
argument-hint: "<ViewName> - name for the new view"
---

# Create SwiftUI View

Scaffold a SwiftUI view with a companion ViewModel using modern Swift patterns.

## Requirements

- Use `@Observable` (NOT `ObservableObject`)
- Use `@State` (NOT `@StateObject`) to own the viewmodel
- Use `@Bindable` when passing observable objects to bindings
- Target Swift 5.9+ / iOS 17+

## Step 1: Detect Project Structure

```bash
# Find existing views to understand naming and directory conventions
find . -name "*View.swift" -not -path "*/.build/*" -not -path "*/Pods/*" | head -20
find . -name "*ViewModel.swift" -not -path "*/.build/*" | head -10
```

Read one existing view to match the project's style (imports, spacing, comment style).

## Step 2: Determine File Locations

Place files following the project's existing convention. Common patterns:
- `Sources/<Feature>/Views/<ViewName>.swift`
- `Sources/<Feature>/ViewModels/<ViewName>ViewModel.swift`
- `<App>/Views/<ViewName>.swift`
- `<App>/Features/<Feature>/<ViewName>.swift`

If no convention is clear, place in a `Views/` directory at the same level as existing views.

## Step 3: Create the ViewModel

Write `<ViewName>ViewModel.swift`:

```swift
import SwiftUI

@Observable
final class <ViewName>ViewModel {
    // MARK: - State

    var isLoading = false
    var errorMessage: String?

    // MARK: - Actions

    func onAppear() {
        // TODO: Implement
    }
}
```

Rules:
- Mark the class `@Observable` and `final`
- Group properties under `// MARK: - State`
- Group methods under `// MARK: - Actions`
- Do NOT add `@Published` -- `@Observable` handles this
- Do NOT conform to `ObservableObject`

## Step 4: Create the View

Write `<ViewName>.swift`:

```swift
import SwiftUI

struct <ViewName>: View {
    @State private var viewModel = <ViewName>ViewModel()

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("<View Name>")
        }
        .task {
            viewModel.onAppear()
        }
    }

    // MARK: - Content

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView()
        } else {
            // TODO: Implement view content
            ContentUnavailableView(
                "<ViewName>",
                systemImage: "square.dashed",
                description: Text("Content goes here")
            )
        }
    }
}

// MARK: - Preview

#Preview {
    <ViewName>()
}
```

Rules:
- Use `@State private var viewModel` (NOT `@StateObject`)
- Use `#Preview` macro (NOT `PreviewProvider`)
- Extract body sections into computed properties when the body exceeds 20 lines
- Use `.task` for async work (NOT `.onAppear`)

## Step 5: Create Test File (Optional)

If the project has a test target, create `<ViewName>ViewModelTests.swift`:

```swift
import Testing
@testable import <ModuleName>

struct <ViewName>ViewModelTests {
    @Test func initialState() {
        let viewModel = <ViewName>ViewModel()
        #expect(viewModel.isLoading == false)
        #expect(viewModel.errorMessage == nil)
    }
}
```

Use Swift Testing (`import Testing`, `@Test`, `#expect`) over XCTest if the project uses Swift 5.9+.

## Report

List created files:
```
Created:
  <path>/<ViewName>.swift           -- SwiftUI view with @State viewModel
  <path>/<ViewName>ViewModel.swift  -- @Observable view model
  <path>/<ViewName>ViewModelTests.swift -- Unit tests (if test target exists)
```
