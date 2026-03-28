# Cross-Platform App Scaffold (macOS + iOS)

> Shared Swift package with platform-specific app targets.

## Workspace Layout

```
AppName/
  Package.swift                    # Root SPM workspace
  SharedKit/                       # Shared Swift package
    Sources/SharedKit/
      API/
        APIClient.swift            # URLSession actor, Bearer auth
        Endpoints.swift            # Endpoint definitions
      Models/
        ContentItem.swift          # SwiftData @Model
        SyncState.swift            # Sync bookkeeping @Model
      Sync/
        SyncEngine.swift           # Background sync orchestrator
        ConflictResolver.swift     # Conflict resolution logic
      Bridge/
        EditorBridge.swift         # WKWebView bridge protocol
        EditorMessage.swift        # Message type definitions
      Types/
        ContentType.swift          # Shared enums
    Tests/SharedKitTests/
  AppNameMac/                      # macOS target
    AppNameMacApp.swift            # @main entry, NavigationSplitView
    Views/                         # macOS-specific views
    Services/                      # Global shortcuts, menus
  AppNameiOS/                      # iOS target
    AppNameiOSApp.swift            # @main entry, TabView
    Views/                         # iOS-specific views
    Extensions/                    # Share Extension, Widget
  EditorBundle/                    # Bundled web editor (if using WKWebView)
    editor.html
    editor.js
    editor.css
    bridge.js
```

## Package.swift

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SharedKit",
    platforms: [.macOS(.v15), .iOS(.v18)],
    products: [
        .library(name: "SharedKit", targets: ["SharedKit"]),
    ],
    targets: [
        .target(name: "SharedKit"),
        .testTarget(name: "SharedKitTests", dependencies: ["SharedKit"]),
    ]
)
```

## What Goes Where

### SharedKit (import by both targets)
- API clients (URLSession actors, endpoint definitions)
- SwiftData @Model definitions (every model, every relationship)
- Sync engine (push/pull, isDirty tracking, conflict resolution)
- Type definitions (enums, constants, configuration)
- Bridge protocols (WKWebView message types, command enums)
- Business logic (validation, transforms, computed values)

### App Targets (platform-specific only)
- Views (NavigationSplitView on macOS, TabView on iOS)
- Platform services (NSEvent monitoring on macOS, WidgetKit on iOS)
- Extensions (Share Extension, Widget Extension: iOS only)
- Platform-specific navigation and window management
- NSViewRepresentable / UIViewRepresentable wrappers

## Setup Steps

1. Create the Package.swift at workspace root
2. Create SharedKit/Sources/SharedKit/ directory structure
3. Move shared code (models, API, sync) into SharedKit
4. In Xcode: each app target adds SharedKit as local package dependency
5. Import SharedKit in app target files: `import SharedKit`
6. Test SharedKit independently: `swift test` in the SharedKit directory
