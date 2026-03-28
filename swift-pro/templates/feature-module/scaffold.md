# Feature Module Template

## Directory Structure

```
Features/
  {FeatureName}/
    Views/
      {FeatureName}View.swift
    ViewModels/
      {FeatureName}ViewModel.swift
    Models/
      {FeatureName}Model.swift      # Optional -- only if feature has domain models
```

## {FeatureName}View.swift

```swift
import SwiftUI

struct {FeatureName}View: View {
    @State private var viewModel = {FeatureName}ViewModel()

    var body: some View {
        content
            .navigationTitle("{Feature Name}")
            .task { await viewModel.onAppear() }
            .alert("Error", isPresented: $viewModel.showError) {
                Button("OK") { viewModel.dismissError() }
            } message: {
                Text(viewModel.errorMessage ?? "Something went wrong.")
            }
    }

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView()
        } else {
            mainContent
        }
    }

    private var mainContent: some View {
        List(viewModel.items) { item in
            Text(item.title)
        }
        .refreshable { await viewModel.refresh() }
    }
}

#Preview {
    NavigationStack {
        {FeatureName}View()
    }
}
```

## {FeatureName}ViewModel.swift

```swift
import Foundation

@Observable
final class {FeatureName}ViewModel {
    // MARK: - Published State

    var items: [{FeatureName}Model] = []
    var isLoading = false
    var showError = false
    var errorMessage: String?

    // MARK: - Dependencies

    private let service: {FeatureName}ServiceProtocol

    init(service: {FeatureName}ServiceProtocol = {FeatureName}Service()) {
        self.service = service
    }

    // MARK: - Actions

    func onAppear() async {
        guard items.isEmpty else { return }
        await load()
    }

    func refresh() async {
        await load()
    }

    func dismissError() {
        showError = false
        errorMessage = nil
    }

    // MARK: - Private

    private func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await service.fetchItems()
        } catch {
            errorMessage = error.localizedDescription
            showError = true
        }
    }
}
```

## {FeatureName}Model.swift (Optional)

```swift
import Foundation
import SwiftData

@Model
final class {FeatureName}Model {
    var id: String
    var title: String
    var createdAt: Date

    init(id: String = UUID().uuidString, title: String, createdAt: Date = .now) {
        self.id = id
        self.title = title
        self.createdAt = createdAt
    }
}
```

## Usage Notes

- Replace `{FeatureName}` with the actual feature name (e.g., `Profile`, `Search`, `Settings`).
- The `Model` file is optional. Omit it when the feature only displays data from other modules.
- Inject dependencies via the ViewModel initializer for testability.
- Keep the View's `body` under 100 lines; extract `@ViewBuilder` helpers for complex layouts.
- Use `@Query` directly in the View when the feature reads SwiftData models without transformation.
