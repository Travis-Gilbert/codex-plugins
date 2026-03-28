# macOS AppKit Patterns

## Window Architecture

### NSWindow Configuration

```swift
class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1200, height: 800),
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        window.title = "My App"
        window.minSize = NSSize(width: 800, height: 600)
        window.center()
        window.setFrameAutosaveName("MainWindow")

        // Modern titlebar configuration
        window.titlebarAppearsTransparent = true
        window.titleVisibility = .hidden
        window.toolbarStyle = .unified  // .unified, .unifiedCompact, .expanded, .preference

        window.contentViewController = MainSplitViewController()
        window.makeKeyAndOrderFront(nil)
    }
}
```

### Style Masks

| Mask | Effect |
|------|--------|
| `.titled` | Window has a title bar |
| `.closable` | Close button (red) |
| `.miniaturizable` | Minimize button (yellow) |
| `.resizable` | Resize control and maximize button (green) |
| `.fullSizeContentView` | Content extends behind title bar |
| `.unifiedTitleAndToolbar` | Title bar and toolbar merge |
| `.borderless` | No chrome at all |

### Window Lifecycle (SwiftUI App)

```swift
@main
struct MyMacApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.hiddenTitleBar)
        .defaultSize(width: 1200, height: 800)
        .windowResizability(.contentMinSize)

        Settings {
            SettingsView()
        }

        Window("Inspector", id: "inspector") {
            InspectorView()
        }
        .defaultPosition(.trailing)
        .defaultSize(width: 300, height: 600)
    }
}
```

---

## NSSplitViewController (3-Pane Layout)

```
┌──────────────────────────────────────────────────────────────┐
│  Toolbar                                                     │
├──────────┬──────────────────────┬────────────────────────────┤
│          │                      │                            │
│ Sidebar  │   Content Area       │   Inspector / Detail       │
│          │                      │                            │
│ 200-250  │   Flexible           │   250-350                  │
│  points  │                      │    points                  │
│          │                      │                            │
│ Source   │   Main content       │   Properties, metadata,    │
│ list,    │   list, editor,      │   actions for selected     │
│ nav      │   canvas, etc.       │   item                     │
│          │                      │                            │
├──────────┴──────────────────────┴────────────────────────────┤
│  Status Bar (optional)                                       │
└──────────────────────────────────────────────────────────────┘
```

```swift
class MainSplitViewController: NSSplitViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Sidebar
        let sidebarItem = NSSplitViewItem(
            sidebarWithViewController: SidebarViewController()
        )
        sidebarItem.minimumThickness = 200
        sidebarItem.maximumThickness = 300
        sidebarItem.canCollapse = true
        sidebarItem.collapseBehavior = .preferResizingSplitViewWithFixedSiblings

        // Content
        let contentItem = NSSplitViewItem(
            contentListWithViewController: ContentViewController()
        )
        contentItem.minimumThickness = 400

        // Inspector
        let inspectorItem = NSSplitViewItem(
            inspectorWithViewController: InspectorViewController()
        )
        inspectorItem.minimumThickness = 250
        inspectorItem.maximumThickness = 400
        inspectorItem.canCollapse = true
        inspectorItem.isCollapsed = true  // Start collapsed

        addSplitViewItem(sidebarItem)
        addSplitViewItem(contentItem)
        addSplitViewItem(inspectorItem)

        splitView.autosaveName = "MainSplitView"
    }

    func toggleInspector() {
        guard splitViewItems.count > 2 else { return }
        let inspector = splitViewItems[2]
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.25
            inspector.animator().isCollapsed.toggle()
        }
    }

    func toggleSidebar() {
        guard let sidebar = splitViewItems.first else { return }
        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.25
            sidebar.animator().isCollapsed.toggle()
        }
    }
}
```

---

## NSOutlineView for Source List Sidebar

```swift
class SidebarViewController: NSViewController, NSOutlineViewDataSource, NSOutlineViewDelegate {
    private let outlineView = NSOutlineView()
    private let scrollView = NSScrollView()

    struct SidebarItem: Hashable {
        let title: String
        let icon: NSImage.Name
        let children: [SidebarItem]

        init(title: String, icon: NSImage.Name, children: [SidebarItem] = []) {
            self.title = title
            self.icon = icon
            self.children = children
        }
    }

    let items: [SidebarItem] = [
        SidebarItem(title: "Library", icon: NSImage.Name("books.vertical"), children: [
            SidebarItem(title: "All Items", icon: NSImage.Name("tray.full")),
            SidebarItem(title: "Favorites", icon: NSImage.Name("heart")),
            SidebarItem(title: "Recent", icon: NSImage.Name("clock")),
        ]),
        SidebarItem(title: "Tags", icon: NSImage.Name("tag"), children: [
            SidebarItem(title: "Work", icon: NSImage.Name("circle.fill")),
            SidebarItem(title: "Personal", icon: NSImage.Name("circle.fill")),
        ]),
    ]

    override func loadView() {
        let column = NSTableColumn(identifier: .init("SidebarColumn"))
        column.title = "Sidebar"
        outlineView.addTableColumn(column)
        outlineView.outlineTableColumn = column
        outlineView.headerView = nil
        outlineView.dataSource = self
        outlineView.delegate = self
        outlineView.style = .sourceList  // Source list appearance
        outlineView.selectionHighlightStyle = .sourceList

        scrollView.documentView = outlineView
        scrollView.hasVerticalScroller = true
        self.view = scrollView
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        outlineView.expandItem(nil, expandChildren: true)
    }

    // MARK: - DataSource

    func outlineView(_ outlineView: NSOutlineView, numberOfChildrenOfItem item: Any?) -> Int {
        guard let sidebarItem = item as? SidebarItem else { return items.count }
        return sidebarItem.children.count
    }

    func outlineView(_ outlineView: NSOutlineView, child index: Int, ofItem item: Any?) -> Any {
        guard let sidebarItem = item as? SidebarItem else { return items[index] }
        return sidebarItem.children[index]
    }

    func outlineView(_ outlineView: NSOutlineView, isItemExpandable item: Any) -> Bool {
        guard let sidebarItem = item as? SidebarItem else { return false }
        return !sidebarItem.children.isEmpty
    }

    // MARK: - Delegate

    func outlineView(_ outlineView: NSOutlineView, viewFor tableColumn: NSTableColumn?, item: Any) -> NSView? {
        guard let sidebarItem = item as? SidebarItem else { return nil }

        let identifier = NSUserInterfaceItemIdentifier("SidebarCell")
        let cell = outlineView.makeView(withIdentifier: identifier, owner: self) as? NSTableCellView
            ?? NSTableCellView()

        cell.identifier = identifier
        cell.textField?.stringValue = sidebarItem.title
        cell.imageView?.image = NSImage(systemSymbolName: String(sidebarItem.icon),
                                         accessibilityDescription: sidebarItem.title)
        return cell
    }

    func outlineView(_ outlineView: NSOutlineView, isGroupItem item: Any) -> Bool {
        guard let sidebarItem = item as? SidebarItem else { return false }
        return !sidebarItem.children.isEmpty  // Top-level groups
    }

    func outlineViewSelectionDidChange(_ notification: Notification) {
        let selectedRow = outlineView.selectedRow
        guard selectedRow >= 0,
              let item = outlineView.item(atRow: selectedRow) as? SidebarItem else { return }
        // Notify content area of selection change
        NotificationCenter.default.post(name: .sidebarSelectionChanged, object: item)
    }
}
```

---

## NSToolbar Configuration

```swift
extension NSToolbarItem.Identifier {
    static let addItem = NSToolbarItem.Identifier("addItem")
    static let search = NSToolbarItem.Identifier("search")
    static let toggleInspector = NSToolbarItem.Identifier("toggleInspector")
    static let viewMode = NSToolbarItem.Identifier("viewMode")
}

class ToolbarDelegate: NSObject, NSToolbarDelegate {
    weak var splitViewController: MainSplitViewController?

    func toolbar(_ toolbar: NSToolbar, itemForItemIdentifier itemIdentifier: NSToolbarItem.Identifier,
                 willBeInsertedIntoToolbar flag: Bool) -> NSToolbarItem? {
        switch itemIdentifier {
        case .addItem:
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.image = NSImage(systemSymbolName: "plus", accessibilityDescription: "Add")
            item.label = "Add"
            item.toolTip = "Add new item"
            item.action = #selector(addItem(_:))
            item.target = self
            return item

        case .search:
            let item = NSSearchToolbarItem(itemIdentifier: itemIdentifier)
            item.searchField.placeholderString = "Search"
            return item

        case .toggleInspector:
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.image = NSImage(systemSymbolName: "sidebar.trailing",
                                  accessibilityDescription: "Toggle Inspector")
            item.label = "Inspector"
            item.action = #selector(toggleInspector(_:))
            item.target = self
            return item

        case .viewMode:
            let group = NSToolbarItemGroup(
                itemIdentifier: itemIdentifier,
                images: [
                    NSImage(systemSymbolName: "list.bullet", accessibilityDescription: "List")!,
                    NSImage(systemSymbolName: "square.grid.2x2", accessibilityDescription: "Grid")!,
                ],
                selectionMode: .selectOne,
                labels: ["List", "Grid"],
                target: self,
                action: #selector(changeViewMode(_:))
            )
            group.selectedIndex = 0
            return group

        default:
            return nil
        }
    }

    func toolbarDefaultItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        [.toggleSidebar, .addItem, .flexibleSpace, .viewMode, .search, .toggleInspector]
    }

    func toolbarAllowedItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        [.toggleSidebar, .addItem, .search, .toggleInspector, .viewMode,
         .flexibleSpace, .space]
    }
}
```

---

## Menu Bar

```swift
class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        setupMenuBar()
    }

    private func setupMenuBar() {
        let mainMenu = NSMenu()

        // App menu
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "About My App", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Settings...", action: #selector(showSettings), keyEquivalent: ",")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Quit My App", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        let appMenuItem = NSMenuItem()
        appMenuItem.submenu = appMenu
        mainMenu.addItem(appMenuItem)

        // File menu
        let fileMenu = NSMenu(title: "File")
        fileMenu.addItem(withTitle: "New", action: #selector(newDocument), keyEquivalent: "n")
        fileMenu.addItem(withTitle: "Open...", action: #selector(openDocument), keyEquivalent: "o")
        fileMenu.addItem(.separator())
        fileMenu.addItem(withTitle: "Export...", action: #selector(exportDocument), keyEquivalent: "e")
        // Modifier keys: command is default, add shift/option
        let exportItem = fileMenu.items.last!
        exportItem.keyEquivalentModifierMask = [.command, .shift]

        let fileMenuItem = NSMenuItem()
        fileMenuItem.submenu = fileMenu
        mainMenu.addItem(fileMenuItem)

        NSApplication.shared.mainMenu = mainMenu
    }
}

// SwiftUI-native menus
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("New Document") { /* ... */ }
                    .keyboardShortcut("n")
                Button("New from Template...") { /* ... */ }
                    .keyboardShortcut("n", modifiers: [.command, .shift])
            }
            CommandMenu("View") {
                Button("Toggle Sidebar") { /* ... */ }
                    .keyboardShortcut("s", modifiers: [.command, .control])
                Button("Toggle Inspector") { /* ... */ }
                    .keyboardShortcut("i", modifiers: [.command, .option])
                Divider()
                Picker("View Mode", selection: $viewMode) {
                    Text("List").tag(ViewMode.list)
                    Text("Grid").tag(ViewMode.grid)
                }
            }
        }
    }
}
```

---

## Hosting SwiftUI in AppKit

### NSHostingController (View Controller)

```swift
class ModernContentViewController: NSViewController {
    override func loadView() {
        let swiftUIView = ContentListView()
        let hostingController = NSHostingController(rootView: swiftUIView)
        addChild(hostingController)
        self.view = hostingController.view
    }
}
```

### NSHostingView (Direct View)

```swift
class HybridViewController: NSViewController {
    override func loadView() {
        let container = NSView()

        // AppKit portion (top)
        let toolbar = NSStackView()
        // ... configure toolbar

        // SwiftUI portion (bottom)
        let hostingView = NSHostingView(rootView: ItemGridView())
        hostingView.translatesAutoresizingMaskIntoConstraints = false

        container.addSubview(toolbar)
        container.addSubview(hostingView)

        NSLayoutConstraint.activate([
            hostingView.topAnchor.constraint(equalTo: toolbar.bottomAnchor),
            hostingView.leadingAnchor.constraint(equalTo: container.leadingAnchor),
            hostingView.trailingAnchor.constraint(equalTo: container.trailingAnchor),
            hostingView.bottomAnchor.constraint(equalTo: container.bottomAnchor),
        ])

        self.view = container
    }
}
```

---

## Bridging @Observable State

Share state between AppKit controllers and SwiftUI views:

```swift
@Observable
class AppState {
    var selectedItem: Item?
    var sidebarSelection: SidebarItem?
    var inspectorVisible: Bool = false
}

// In AppKit
class SidebarViewController: NSViewController {
    var appState: AppState

    init(appState: AppState) {
        self.appState = appState
        super.init(nibName: nil, bundle: nil)
    }

    func outlineViewSelectionDidChange(_ notification: Notification) {
        appState.sidebarSelection = selectedSidebarItem
    }
}

// In SwiftUI hosted view
struct ContentListView: View {
    @Bindable var appState: AppState

    var body: some View {
        List(selection: $appState.selectedItem) {
            // ...
        }
    }
}
```

---

## Window Restoration

```swift
class AppDelegate: NSObject, NSApplicationDelegate {
    func application(_ app: NSApplication, willEncodeRestorableState coder: NSCoder) {
        // Save custom state
        if let data = try? JSONEncoder().encode(appState) {
            coder.encode(data, forKey: "appState")
        }
    }

    func application(_ app: NSApplication, didDecodeRestorableState coder: NSCoder) {
        if let data = coder.decodeObject(forKey: "appState") as? Data,
           let state = try? JSONDecoder().decode(AppState.self, from: data) {
            self.appState = state
        }
    }
}

// Window controllers restore via NSWindowRestoration
class MainWindowController: NSWindowController, NSWindowDelegate {
    override var windowFrameAutosaveName: NSWindow.FrameAutosaveName { "MainWindow" }
}
```

---

## Status Bar (Menu Bar Extra)

```swift
// SwiftUI approach
@main
struct MyApp: App {
    var body: some Scene {
        MenuBarExtra("My App", systemImage: "star.fill") {
            Button("Show Dashboard") { /* ... */ }
            Button("Quick Add...") { /* ... */ }
            Divider()
            Button("Quit") { NSApp.terminate(nil) }
        }
        .menuBarExtraStyle(.menu)  // .menu or .window

        // Window-style for richer UI
        MenuBarExtra("Status", systemImage: "chart.bar") {
            StatusDashboardView()
                .frame(width: 300, height: 400)
        }
        .menuBarExtraStyle(.window)
    }
}

// AppKit approach for more control
class StatusBarController {
    private var statusItem: NSStatusItem!

    init() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.image = NSImage(systemSymbolName: "star.fill",
                                            accessibilityDescription: "My App")
        statusItem.menu = buildMenu()
    }

    private func buildMenu() -> NSMenu {
        let menu = NSMenu()
        menu.addItem(withTitle: "Show Dashboard", action: #selector(showDashboard), keyEquivalent: "d")
        menu.addItem(.separator())
        menu.addItem(withTitle: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        return menu
    }
}
```
