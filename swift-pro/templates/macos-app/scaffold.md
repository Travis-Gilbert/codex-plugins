# macOS App Scaffold -- AppKit + SwiftUI Hybrid

## Directory Structure

```
AppName/
  AppDelegate.swift           # NSApplicationDelegate
  MainWindowController.swift  # NSWindowController setup
  MainSplitViewController.swift  # 3-pane NSSplitViewController
  SidebarViewController.swift    # NSOutlineView source list
  ContentListViewController.swift # Middle pane
  DetailHostingController.swift  # NSHostingController for SwiftUI detail
  ToolbarController.swift        # NSToolbar configuration
  MenuBuilder.swift              # Main menu setup

  SwiftUI/
    DetailView.swift             # SwiftUI detail pane
    InspectorView.swift          # SwiftUI inspector panel

  Models/
    SidebarItem.swift
    Document.swift

  Resources/
    Assets.xcassets
    MainMenu.xib                 # Or build menus programmatically
```

## NSWindow Setup

```swift
import AppKit

final class MainWindowController: NSWindowController {
    convenience init() {
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1200, height: 800),
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.title = "AppName"
        window.titlebarAppearsTransparent = false
        window.toolbarStyle = .unified
        window.setFrameAutosaveName("MainWindow")
        window.minSize = NSSize(width: 800, height: 500)
        window.center()

        self.init(window: window)

        let splitVC = MainSplitViewController()
        window.contentViewController = splitVC
        configureToolbar(for: window)
    }

    private func configureToolbar(for window: NSWindow) {
        let toolbar = NSToolbar(identifier: "MainToolbar")
        toolbar.delegate = ToolbarController.shared
        toolbar.displayMode = .iconOnly
        toolbar.allowsUserCustomization = true
        toolbar.autosavesConfiguration = true
        window.toolbar = toolbar
    }
}
```

## NSSplitViewController 3-Pane Layout

```swift
import AppKit

final class MainSplitViewController: NSSplitViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Sidebar (source list)
        let sidebarItem = NSSplitViewItem(
            sidebarWithViewController: SidebarViewController()
        )
        sidebarItem.canCollapse = true
        sidebarItem.minimumThickness = 200
        sidebarItem.maximumThickness = 300
        sidebarItem.holdingPriority = .defaultLow + 1

        // Content list (middle)
        let contentItem = NSSplitViewItem(
            contentListWithViewController: ContentListViewController()
        )
        contentItem.minimumThickness = 250

        // Detail (SwiftUI hosted)
        let detailItem = NSSplitViewItem(
            viewController: DetailHostingController()
        )
        detailItem.minimumThickness = 400

        addSplitViewItem(sidebarItem)
        addSplitViewItem(contentItem)
        addSplitViewItem(detailItem)

        splitView.autosaveName = "MainSplitView"
    }
}
```

## NSOutlineView Sidebar

```swift
import AppKit

final class SidebarViewController: NSViewController,
    NSOutlineViewDataSource, NSOutlineViewDelegate {

    private let outlineView = NSOutlineView()
    private let scrollView = NSScrollView()

    var items: [SidebarItem] = SidebarItem.defaultItems

    override func loadView() {
        scrollView.documentView = outlineView
        scrollView.hasVerticalScroller = true
        self.view = scrollView

        outlineView.dataSource = self
        outlineView.delegate = self
        outlineView.style = .sourceList
        outlineView.headerView = nil
        outlineView.rowSizeStyle = .default

        let column = NSTableColumn(identifier: .init("SidebarColumn"))
        column.isEditable = false
        outlineView.addTableColumn(column)
        outlineView.outlineTableColumn = column
    }

    // MARK: - NSOutlineViewDataSource

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

    // MARK: - NSOutlineViewDelegate

    func outlineView(_ outlineView: NSOutlineView, viewFor tableColumn: NSTableColumn?, item: Any) -> NSView? {
        guard let sidebarItem = item as? SidebarItem else { return nil }
        let cell = NSTableCellView()
        let textField = NSTextField(labelWithString: sidebarItem.title)
        let imageView = NSImageView(image: NSImage(systemSymbolName: sidebarItem.icon, accessibilityDescription: nil) ?? NSImage())
        cell.textField = textField
        cell.imageView = imageView
        cell.addSubview(imageView)
        cell.addSubview(textField)
        return cell
    }

    func outlineViewSelectionDidChange(_ notification: Notification) {
        let row = outlineView.selectedRow
        guard row >= 0, let item = outlineView.item(atRow: row) as? SidebarItem else { return }
        NotificationCenter.default.post(name: .sidebarSelectionChanged, object: item)
    }
}
```

## NSToolbar Configuration

```swift
import AppKit

final class ToolbarController: NSObject, NSToolbarDelegate {
    static let shared = ToolbarController()

    private enum ToolbarItemID {
        static let addItem = NSToolbarItem.Identifier("addItem")
        static let share = NSToolbarItem.Identifier("share")
        static let search = NSToolbarItem.Identifier("search")
        static let toggleSidebar = NSToolbarItem.Identifier("toggleSidebar")
    }

    func toolbarDefaultItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        [
            ToolbarItemID.toggleSidebar,
            .flexibleSpace,
            ToolbarItemID.addItem,
            ToolbarItemID.share,
            .flexibleSpace,
            ToolbarItemID.search,
        ]
    }

    func toolbarAllowedItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        toolbarDefaultItemIdentifiers(toolbar) + [.space]
    }

    func toolbar(_ toolbar: NSToolbar, itemForItemIdentifier itemIdentifier: NSToolbarItem.Identifier, willBeInsertedIntoToolbar flag: Bool) -> NSToolbarItem? {
        switch itemIdentifier {
        case ToolbarItemID.toggleSidebar:
            return NSToolbarItem(itemIdentifier: .toggleSidebar)
        case ToolbarItemID.addItem:
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.image = NSImage(systemSymbolName: "plus", accessibilityDescription: "Add")
            item.label = "Add"
            item.action = #selector(AppDelegate.addItem(_:))
            return item
        case ToolbarItemID.search:
            let item = NSSearchToolbarItem(itemIdentifier: itemIdentifier)
            item.searchField.placeholderString = "Search"
            return item
        default:
            return nil
        }
    }
}
```

## SwiftUI Hosting via NSHostingController

```swift
import AppKit
import SwiftUI

final class DetailHostingController: NSHostingController<DetailView> {
    init() {
        super.init(rootView: DetailView())
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }
}
```

## Menu Bar Setup

```swift
import AppKit

extension AppDelegate {
    func buildMainMenu() -> NSMenu {
        let mainMenu = NSMenu()

        // App menu
        let appMenuItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "About AppName", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Settings...", action: #selector(showSettings(_:)), keyEquivalent: ",")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Quit AppName", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appMenuItem.submenu = appMenu
        mainMenu.addItem(appMenuItem)

        // File menu
        let fileMenuItem = NSMenuItem()
        let fileMenu = NSMenu(title: "File")
        fileMenu.addItem(withTitle: "New", action: #selector(newDocument(_:)), keyEquivalent: "n")
        fileMenu.addItem(withTitle: "Open...", action: #selector(openDocument(_:)), keyEquivalent: "o")
        fileMenuItem.submenu = fileMenu
        mainMenu.addItem(fileMenuItem)

        // Edit menu
        let editMenuItem = NSMenuItem()
        let editMenu = NSMenu(title: "Edit")
        editMenu.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        editMenu.addItem(withTitle: "Redo", action: Selector(("redo:")), keyEquivalent: "Z")
        editMenuItem.submenu = editMenu
        mainMenu.addItem(editMenuItem)

        return mainMenu
    }
}
```

## Conventions

- Use AppKit for window chrome, toolbars, menus, and outline views.
- Use SwiftUI via NSHostingController for content panes and detail views.
- Prefer `@Observable` for shared state between AppKit and SwiftUI.
- Use `NSSplitViewItem` factory methods (`sidebarWithViewController`, `contentListWithViewController`) for proper styling.
- Set `autosaveName` on both windows and split views for layout persistence.
