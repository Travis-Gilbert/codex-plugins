# NSWindow Reference

## Window Creation

```swift
let window = NSWindow(
    contentRect: NSRect(x: 0, y: 0, width: 1200, height: 800),
    styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
    backing: .buffered,
    defer: false
)
```

## Style Mask Options

| Mask | Purpose |
|------|---------|
| `.titled` | Title bar with title |
| `.closable` | Close button |
| `.miniaturizable` | Minimize button |
| `.resizable` | Resize control |
| `.fullSizeContentView` | Content extends behind titlebar |
| `.borderless` | No chrome (utility windows) |
| `.unifiedTitleAndToolbar` | Legacy unified style |
| `.fullScreen` | Supports full screen mode |

## Titlebar Configuration

```swift
// Transparent titlebar (content shows through)
window.titlebarAppearsTransparent = true

// Hide title text
window.titleVisibility = .hidden

// Full-size content view (content extends behind titlebar)
window.styleMask.insert(.fullSizeContentView)

// Title + subtitle
window.title = "My Document"
window.subtitle = "Last saved 2 minutes ago"

// Title with represented file
window.representedURL = fileURL
window.title = fileURL.lastPathComponent
```

## Toolbar Styles

```swift
window.toolbarStyle = .unified          // Default: toolbar merged into titlebar
window.toolbarStyle = .unifiedCompact   // Compact merged
window.toolbarStyle = .expanded         // Toolbar below titlebar
window.toolbarStyle = .preference       // Settings-style centered
window.toolbarStyle = .automatic        // System-chosen
```

## Window Sizing

```swift
window.minSize = NSSize(width: 800, height: 500)
window.maxSize = NSSize(width: 2400, height: 1600)
window.setContentSize(NSSize(width: 1200, height: 800))
window.center()  // Center on screen

// Frame autosave (persists position/size)
window.setFrameAutosaveName("MainWindow")

// Aspect ratio lock
window.aspectRatio = NSSize(width: 16, height: 9)
```

## Tab Support

```swift
// Enable window tabbing
window.tabbingMode = .automatic   // System default
window.tabbingMode = .preferred   // Encourage tabs
window.tabbingMode = .disallowed  // No tabs

// Tab identifier (windows with same ID can tab together)
window.tabbingIdentifier = "DocumentWindow"

// Merge all windows into tabs
window.mergeAllWindows(nil)
```

## Window Restoration

```swift
// Enable state restoration
window.isRestorable = true
window.restorationClass = MainWindowController.self

// In the restoration class:
extension MainWindowController: NSWindowRestoration {
    static func restoreWindow(
        withIdentifier identifier: NSUserInterfaceItemIdentifier,
        state: NSCoder,
        completionHandler: @escaping (NSWindow?, Error?) -> Void
    ) {
        let controller = MainWindowController()
        controller.window?.setFrameAutosaveName("MainWindow")
        completionHandler(controller.window, nil)
    }
}
```

## Sheets

```swift
// Present a sheet
window.beginSheet(sheetWindow) { response in
    switch response {
    case .OK:     handleConfirm()
    case .cancel: handleCancel()
    default:      break
    }
}

// Or from a view controller
presentAsSheet(someViewController)

// End a sheet
window.endSheet(sheetWindow, returnCode: .OK)
```

## Window Levels

```swift
window.level = .normal           // Default
window.level = .floating         // Above normal windows
window.level = .statusBar        // Above floating
window.level = .modalPanel       // Modal panels
window.level = .mainMenu         // Menu level
window.level = .popUpMenu        // Popup menus
```

## Appearance

```swift
// Force light/dark mode
window.appearance = NSAppearance(named: .darkAqua)
window.appearance = NSAppearance(named: .aqua)
window.appearance = nil  // Follow system

// Background color
window.backgroundColor = .windowBackgroundColor

// Opacity
window.isOpaque = true
window.alphaValue = 1.0  // 0.0 to 1.0

// Movable by background
window.isMovableByWindowBackground = true
```

## Key and Main Window

```swift
window.makeKeyAndOrderFront(nil)  // Show and make key
window.makeKey()                   // Make key without ordering
window.orderFront(nil)            // Show without making key

// Check status
window.isKeyWindow    // Receives keyboard input
window.isMainWindow   // Primary document window

// Notifications
NotificationCenter.default.addObserver(
    forName: NSWindow.didBecomeKeyNotification,
    object: window, queue: .main
) { _ in
    // Window became key
}
```

## Window Delegate

```swift
extension MainWindowController: NSWindowDelegate {
    func windowWillClose(_ notification: Notification) {
        // Cleanup
    }

    func windowShouldClose(_ sender: NSWindow) -> Bool {
        return !hasUnsavedChanges || confirmDiscard()
    }

    func windowDidResize(_ notification: Notification) { }

    func windowWillEnterFullScreen(_ notification: Notification) { }
    func windowDidEnterFullScreen(_ notification: Notification) { }
    func windowWillExitFullScreen(_ notification: Notification) { }
}
```

## Common Patterns

- Use `.fullSizeContentView` + `titlebarAppearsTransparent` for modern appearance.
- Set `setFrameAutosaveName` early so window position persists.
- Use `tabbingIdentifier` for windows that should be tabbable together.
- Use `window.subtitle` for document status (e.g., save state, word count).
- Handle `windowShouldClose` for unsaved-changes dialogs.
