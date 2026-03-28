---
description: Scaffold a complete feature module
allowed-tools: Read, Write, Glob, Bash
argument-hint: "<FeatureName> - name for the feature module"
---

# Create Feature Module

Scaffold a complete feature module with views, viewmodels, models, and test stubs.

## Step 1: Detect Project Structure

```bash
# Find existing feature directories
find . -type d -name "Features" -not -path "*/.build/*" | head -5
find . -type d -name "Views" -not -path "*/.build/*" | head -10

# Check for existing feature modules to match conventions
ls -d */Features/*/ 2>/dev/null || ls -d Sources/*/Features/*/ 2>/dev/null || echo "No existing features"

# Find the test target directory
find . -type d -name "*Tests" -not -path "*/.build/*" -not -path "*/Pods/*" | head -5
```

Read one existing feature module (if any) to match the project's conventions for directory structure, naming, and imports.

## Step 2: Create Directory Structure

Create the feature module directory tree:

```
Features/<FeatureName>/
  Views/
  ViewModels/
  Models/
```

If the project uses a different convention (e.g., flat structure, `Sources/<App>/Features/`), follow that instead.

```bash
mkdir -p <BasePath>/Features/<FeatureName>/Views
mkdir -p <BasePath>/Features/<FeatureName>/ViewModels
mkdir -p <BasePath>/Features/<FeatureName>/Models
```

## Step 3: Create the Model

Write `Models/<FeatureName>.swift`:

```swift
import Foundation

struct <FeatureName>: Identifiable, Hashable, Sendable {
    let id: UUID
    // TODO: Add domain properties

    init(id: UUID = UUID()) {
        self.id = id
    }
}
```

Rules:
- Conform to `Identifiable`, `Hashable`, `Sendable`
- Use value types (struct) unless reference semantics are required
- Include a default `UUID()` initializer

## Step 4: Create the ViewModel

Write `ViewModels/<FeatureName>ViewModel.swift`:

```swift
import SwiftUI

@Observable
final class <FeatureName>ViewModel {
    // MARK: - State

    var items: [<FeatureName>] = []
    var isLoading = false
    var errorMessage: String?

    // MARK: - Actions

    func onAppear() async {
        isLoading = true
        defer { isLoading = false }
        // TODO: Load data
    }

    func add(_ item: <FeatureName>) {
        items.append(item)
    }

    func delete(at offsets: IndexSet) {
        items.remove(atOffsets: offsets)
    }
}
```

Use `@Observable` (NOT `ObservableObject`).

## Step 5: Create the View

Write `Views/<FeatureName>View.swift`:

```swift
import SwiftUI

struct <FeatureName>View: View {
    @State private var viewModel = <FeatureName>ViewModel()

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("<Feature Name>")
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button("Add", systemImage: "plus") {
                            // TODO: Add action
                        }
                    }
                }
        }
        .task {
            await viewModel.onAppear()
        }
    }

    // MARK: - Content

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView()
        } else if viewModel.items.isEmpty {
            ContentUnavailableView(
                "No Items",
                systemImage: "tray",
                description: Text("Add your first item to get started.")
            )
        } else {
            List {
                ForEach(viewModel.items) { item in
                    Text(item.id.uuidString)
                }
                .onDelete { offsets in
                    viewModel.delete(at: offsets)
                }
            }
        }
    }
}

// MARK: - Preview

#Preview {
    <FeatureName>View()
}
```

Use `@State` (NOT `@StateObject`), `#Preview` (NOT `PreviewProvider`).

## Step 6: Create Test Stubs

Write `<FeatureName>ViewModelTests.swift` in the test target:

```swift
import Testing
@testable import <ModuleName>

struct <FeatureName>ViewModelTests {
    @Test func initialState() {
        let viewModel = <FeatureName>ViewModel()
        #expect(viewModel.items.isEmpty)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.errorMessage == nil)
    }

    @Test func addItem() {
        let viewModel = <FeatureName>ViewModel()
        let item = <FeatureName>()
        viewModel.add(item)
        #expect(viewModel.items.count == 1)
    }

    @Test func deleteItem() {
        let viewModel = <FeatureName>ViewModel()
        let item = <FeatureName>()
        viewModel.add(item)
        viewModel.delete(at: IndexSet(integer: 0))
        #expect(viewModel.items.isEmpty)
    }
}
```

Use Swift Testing (`import Testing`, `@Test`, `#expect`) over XCTest.

## Report

```
Feature Module: <FeatureName>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Created:
  <path>/Features/<FeatureName>/Models/<FeatureName>.swift
  <path>/Features/<FeatureName>/ViewModels/<FeatureName>ViewModel.swift
  <path>/Features/<FeatureName>/Views/<FeatureName>View.swift
  <test-path>/<FeatureName>ViewModelTests.swift

Next steps:
  1. Add domain properties to the model
  2. Implement data loading in the ViewModel
  3. Design the view layout
  4. Register the feature's root view in your app navigation
```
