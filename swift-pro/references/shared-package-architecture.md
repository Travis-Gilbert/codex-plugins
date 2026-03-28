# SPM Shared Package Architecture for macOS + iOS

## Overview

A Swift Package Manager shared package keeps business logic, models, networking,
and sync in one place. Platform-specific code (views, navigation) stays in app targets.

---

## Workspace Layout

```
CommonPlace/
├── CommonPlace.xcodeproj
├── StudioKit/                          # Shared SPM package
│   ├── Package.swift
│   ├── Sources/StudioKit/
│   │   ├── Models/                     # @Model classes, ContainerSetup
│   │   ├── Sync/                       # SyncEngine, SyncState, ConflictResolver
│   │   ├── API/                        # APIClient, ServerModels, TokenStore
│   │   ├── Bridge/                     # EditorBridge, EditorCommand, MessageTypes
│   │   └── Utilities/                  # KeychainHelper, DateFormatting
│   └── Tests/StudioKitTests/
├── CommonPlaceMac/                     # macOS app target
│   ├── App/CommonPlaceMacApp.swift
│   ├── Views/                          # SidebarView, EditorContainer, Settings
│   ├── Platform/                       # NSViewRepresentable, GlobalShortcuts, MenuBar
│   └── Extensions/
├── CommonPlaceiOS/                     # iOS app target
│   ├── App/CommonPlaceiOSApp.swift
│   ├── Views/                          # NoteList, EditorContainer, Settings
│   ├── Platform/                       # UIViewRepresentable, ShareExtension
│   └── Extensions/
├── EditorBundle/                       # Bundled web editor (shared)
│   ├── index.html, editor.js, editor.css
└── CommonPlaceWidgets/                 # WidgetKit (iOS)
```

---

## What Goes Where

### In the Shared Package (StudioKit)

| Component | Why |
|-----------|-----|
| `@Model` classes | Single source of truth for schema |
| `ModelContainer` setup | Both platforms use same config |
| `SyncEngine` actor | Sync logic is platform-independent |
| `APIClient` actor | Network calls are identical |
| Server DTOs (Codable) | Shared serialization |
| Token storage (Keychain) | Both platforms use Keychain |
| `EditorBridge` + `EditorCommand` | Bridge protocol is platform-neutral |
| Business logic / validation | Reusable rules |

### In App Targets

| Component | Why |
|-----------|-----|
| `NSViewRepresentable` / `UIViewRepresentable` | Platform-specific API |
| `NavigationSplitView` (macOS) / `TabView` (iOS) | Platform navigation idiom |
| Menu bar commands (macOS) | macOS-only `CommandMenu` |
| Global keyboard shortcuts (macOS) | macOS-only `CGEvent` taps |
| Share Extension (iOS) | iOS-only extension |
| WidgetKit (iOS) | iOS-only |
| App lifecycle (`@main`) | Different Scene configurations |

---

## Package.swift

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "StudioKit",
    platforms: [.macOS(.v15), .iOS(.v18)],
    products: [
        .library(name: "StudioKit", targets: ["StudioKit"]),
    ],
    targets: [
        .target(
            name: "StudioKit",
            swiftSettings: [.enableExperimentalFeature("StrictConcurrency")]
        ),
        .testTarget(name: "StudioKitTests", dependencies: ["StudioKit"]),
    ]
)
```

| Setting | Why |
|---------|-----|
| `.macOS(.v15)`, `.iOS(.v18)` | SwiftData, Observable, modern APIs |
| `StrictConcurrency` | Catch data races at compile time |

---

## Local Package in Xcode

1. Project settings > "Package Dependencies" > "+" > "Add Local..." > select `StudioKit/`
2. Each target > "General" > "Frameworks" > "+" > add `StudioKit`

Verify: `import StudioKit` compiles in both app targets.

---

## ModelContainer Setup in Shared Package

```swift
public enum StudioContainer {
    public static func create(inMemory: Bool = false) throws -> ModelContainer {
        let schema = Schema([ContentItem.self, Workspace.self, Tag.self, SyncTombstone.self])
        let config = ModelConfiguration(
            "StudioStore", schema: schema,
            isStoredInMemoryOnly: inMemory,
            groupContainer: .identifier("group.com.example.commonplace")
        )
        return try ModelContainer(for: schema, configurations: config)
    }
}
```

Using App Group `groupContainer` lets the main app and extensions (widgets, share
extension) share the same SwiftData store. Both targets and extensions must have
the same App Group entitlement.

```swift
// Both app targets — identical container setup
@main
struct CommonPlaceMacApp: App {
    let container = try! StudioContainer.create()
    var body: some Scene {
        WindowGroup { ContentView().modelContainer(container) }
    }
}
```

---

## Conditional Compilation

```swift
#if canImport(AppKit)
import AppKit
#elseif canImport(UIKit)
import UIKit
#endif

extension StudioKit {
    static func openURL(_ url: URL) {
        #if canImport(AppKit)
        NSWorkspace.shared.open(url)
        #elseif canImport(UIKit)
        Task { @MainActor in await UIApplication.shared.open(url) }
        #endif
    }
}
```

Use sparingly. If the conditional block is more than a few lines, the code
belongs in the app target. Use protocol injection for platform-specific behavior:

```swift
// StudioKit defines the protocol
public protocol PlatformServices: Sendable {
    func openURL(_ url: URL) async
    func showNotification(title: String, body: String) async
    func copyToClipboard(_ text: String)
}

// App target provides the implementation
struct MacPlatformServices: PlatformServices {
    func openURL(_ url: URL) async { NSWorkspace.shared.open(url) }
    func showNotification(title: String, body: String) async { /* UNUserNotificationCenter */ }
    func copyToClipboard(_ text: String) {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text, forType: .string)
    }
}
```

---

## Testing Independently

```bash
cd StudioKit && swift test                    # all tests
cd StudioKit && swift test --filter SyncEngineTests  # specific suite
```

```swift
import Testing
@testable import StudioKit

@Suite("SyncEngine Tests")
struct SyncEngineTests {
    @Test("Push dirty records sends to server")
    func pushDirtyRecords() async throws {
        let container = try ModelContainer(
            for: ContentItem.self,
            configurations: ModelConfiguration(isStoredInMemoryOnly: true)
        )
        let mockAPI = MockAPIClient()
        let engine = SyncEngine(modelContainer: container, apiClient: mockAPI)

        let context = ModelContext(container)
        context.insert(ContentItem(title: "Test", body: "Body"))
        try context.save()

        await engine.sync()
        #expect(mockAPI.createdItems.count == 1)
    }
}
```

In-memory `ModelConfiguration` keeps tests fast and isolated.

---

## Trade-offs: SPM Package vs Xcode Framework Target

| Aspect | SPM Package | Xcode Framework |
|--------|-------------|-----------------|
| Setup | Lower — `Package.swift` | Higher — scheme, build settings, signing |
| Independent testing | `swift test` from CLI | Requires Xcode test scheme |
| External deps | Package.swift | CocoaPods/Carthage or manual |
| Cross-platform | `.platforms` in Package.swift | Separate targets per platform |
| Code boundary | Enforced module boundary | Can leak across targets |
| Static vs dynamic | Static by default (better for apps) | Choose either |

**Recommendation:** SPM packages for new projects. They enforce cleaner
boundaries and are the standard approach.

---

## Common Pitfalls

**1. Forgetting `public` access** — SPM enforces access control. Types and methods
used by app targets must be explicitly `public`.

**2. Importing SwiftUI in shared package** — Use `@Observable` (Observation framework)
instead of `@ObservableObject` (Combine/SwiftUI) to avoid unnecessary coupling.

**3. Circular dependencies** — If the shared package needs something from an app
target, use protocol injection. The package must be self-contained.

**4. Missing App Group entitlement** — If using `groupContainer`, all targets AND
extensions must have the same App Group. Without it, each gets a separate database.
