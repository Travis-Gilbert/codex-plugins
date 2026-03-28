# NSToolbar Reference

## Basic Setup

```swift
let toolbar = NSToolbar(identifier: "MainToolbar")
toolbar.delegate = self
toolbar.displayMode = .iconOnly          // .iconOnly, .iconAndLabel, .labelOnly
toolbar.allowsUserCustomization = true   // User can rearrange items
toolbar.autosavesConfiguration = true    // Persist customization
window.toolbar = toolbar
```

## Toolbar Styles (macOS 11+)

```swift
window.toolbarStyle = .unified          // Merged with titlebar (default for new apps)
window.toolbarStyle = .unifiedCompact   // Compact merged
window.toolbarStyle = .expanded         // Below titlebar
window.toolbarStyle = .preference       // Centered icons (for Settings windows)
window.toolbarStyle = .automatic        // System decides
```

## Item Identifiers

```swift
extension NSToolbarItem.Identifier {
    static let addItem = NSToolbarItem.Identifier("addItem")
    static let deleteItem = NSToolbarItem.Identifier("deleteItem")
    static let shareItem = NSToolbarItem.Identifier("shareItem")
    static let searchItem = NSToolbarItem.Identifier("searchItem")
    static let filterItem = NSToolbarItem.Identifier("filterItem")
}
```

## NSToolbarDelegate

```swift
final class ToolbarDelegate: NSObject, NSToolbarDelegate {

    // Default items (shown initially)
    func toolbarDefaultItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        [
            .toggleSidebar,           // Built-in sidebar toggle
            .flexibleSpace,
            .addItem,
            .deleteItem,
            .flexibleSpace,
            .searchItem,
        ]
    }

    // All allowed items (superset of default, for customization palette)
    func toolbarAllowedItemIdentifiers(_ toolbar: NSToolbar) -> [NSToolbarItem.Identifier] {
        [
            .toggleSidebar,
            .addItem,
            .deleteItem,
            .shareItem,
            .searchItem,
            .filterItem,
            .flexibleSpace,
            .space,
        ]
    }

    // Create items
    func toolbar(_ toolbar: NSToolbar,
                 itemForItemIdentifier itemIdentifier: NSToolbarItem.Identifier,
                 willBeInsertedIntoToolbar flag: Bool) -> NSToolbarItem? {

        switch itemIdentifier {
        case .toggleSidebar:
            return NSToolbarItem(itemIdentifier: .toggleSidebar)

        case .addItem:
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.label = "Add"
            item.paletteLabel = "Add Item"
            item.toolTip = "Add a new item"
            item.image = NSImage(systemSymbolName: "plus", accessibilityDescription: "Add")
            item.action = #selector(AppCommands.addItem(_:))
            item.isBordered = true
            return item

        case .deleteItem:
            let item = NSToolbarItem(itemIdentifier: itemIdentifier)
            item.label = "Delete"
            item.image = NSImage(systemSymbolName: "trash", accessibilityDescription: "Delete")
            item.action = #selector(AppCommands.deleteItem(_:))
            item.isBordered = true
            return item

        case .shareItem:
            let item = NSSharingServicePickerToolbarItem(itemIdentifier: itemIdentifier)
            item.label = "Share"
            item.delegate = self
            return item

        case .searchItem:
            let item = NSSearchToolbarItem(itemIdentifier: itemIdentifier)
            item.searchField.placeholderString = "Search"
            item.searchField.delegate = self
            return item

        case .filterItem:
            // Menu-style toolbar item
            let item = NSMenuToolbarItem(itemIdentifier: itemIdentifier)
            item.label = "Filter"
            item.image = NSImage(systemSymbolName: "line.3.horizontal.decrease", accessibilityDescription: "Filter")
            item.menu = makeFilterMenu()
            item.showsIndicator = true
            return item

        default:
            return nil
        }
    }
}
```

## Built-In Identifiers

| Identifier | Purpose |
|-----------|---------|
| `.toggleSidebar` | Toggle NSSplitViewController sidebar |
| `.cloudSharing` | CloudKit sharing |
| `.print` | Print action |
| `.flexibleSpace` | Expanding space between items |
| `.space` | Fixed-width space |
| `.showColors` | Color panel |
| `.showFonts` | Font panel |
| `.toggleInspector` | Toggle inspector pane |

## Search Toolbar Item

```swift
let search = NSSearchToolbarItem(itemIdentifier: .searchItem)
search.searchField.placeholderString = "Search"
search.searchField.delegate = self         // NSSearchFieldDelegate
search.searchField.sendsWholeSearchString = false
search.searchField.sendsSearchStringImmediately = true

// Handle search via delegate:
extension ToolbarDelegate: NSSearchFieldDelegate {
    func controlTextDidChange(_ notification: Notification) {
        guard let searchField = notification.object as? NSSearchField else { return }
        let query = searchField.stringValue
        // Perform search
    }
}
```

## Segmented Control in Toolbar

```swift
let item = NSToolbarItemGroup(
    itemIdentifier: .init("viewMode"),
    images: [
        NSImage(systemSymbolName: "list.bullet", accessibilityDescription: "List")!,
        NSImage(systemSymbolName: "square.grid.2x2", accessibilityDescription: "Grid")!,
    ],
    selectionMode: .selectOne,
    labels: ["List", "Grid"],
    target: self,
    action: #selector(viewModeChanged(_:))
)
item.selectedIndex = 0
```

## Validation

```swift
// Toolbar items auto-validate via NSToolbarItemValidation
extension MainWindowController: NSToolbarItemValidation {
    func validateToolbarItem(_ item: NSToolbarItem) -> Bool {
        switch item.itemIdentifier {
        case .deleteItem:
            return hasSelection
        default:
            return true
        }
    }
}
```

## Toolbar in SwiftUI (macOS)

```swift
struct ContentView: View {
    var body: some View {
        NavigationSplitView { ... } detail: { ... }
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: addItem) {
                        Label("Add", systemImage: "plus")
                    }
                }
                ToolbarItem(placement: .automatic) {
                    Button(action: deleteItem) {
                        Label("Delete", systemImage: "trash")
                    }
                }
            }
    }
}
```
