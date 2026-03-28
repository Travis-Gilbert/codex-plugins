# NSOutlineView Reference

## Source List Setup

```swift
final class SidebarVC: NSViewController, NSOutlineViewDataSource, NSOutlineViewDelegate {
    private let outlineView = NSOutlineView()
    private let scrollView = NSScrollView()
    var rootItems: [SidebarItem] = []

    override func loadView() {
        scrollView.documentView = outlineView
        scrollView.hasVerticalScroller = true
        view = scrollView

        outlineView.style = .sourceList           // Source list appearance
        outlineView.headerView = nil              // No column header
        outlineView.rowSizeStyle = .default
        outlineView.selectionHighlightStyle = .sourceList
        outlineView.floatsGroupRows = false

        let column = NSTableColumn(identifier: .init("Main"))
        column.isEditable = false
        outlineView.addTableColumn(column)
        outlineView.outlineTableColumn = column

        outlineView.dataSource = self
        outlineView.delegate = self
    }
}
```

## Data Model

```swift
class SidebarItem {
    let id: String
    let title: String
    let icon: String           // SF Symbol name
    var children: [SidebarItem]
    var isGroup: Bool          // Section headers

    init(title: String, icon: String = "", children: [SidebarItem] = [], isGroup: Bool = false) {
        self.id = UUID().uuidString
        self.title = title
        self.icon = icon
        self.children = children
        self.isGroup = isGroup
    }
}
```

## NSOutlineViewDataSource

```swift
// Number of children for an item (nil = root)
func outlineView(_ outlineView: NSOutlineView, numberOfChildrenOfItem item: Any?) -> Int {
    guard let sidebarItem = item as? SidebarItem else {
        return rootItems.count
    }
    return sidebarItem.children.count
}

// Child at index
func outlineView(_ outlineView: NSOutlineView, child index: Int, ofItem item: Any?) -> Any {
    guard let sidebarItem = item as? SidebarItem else {
        return rootItems[index]
    }
    return sidebarItem.children[index]
}

// Is expandable?
func outlineView(_ outlineView: NSOutlineView, isItemExpandable item: Any) -> Bool {
    guard let sidebarItem = item as? SidebarItem else { return false }
    return !sidebarItem.children.isEmpty
}
```

## NSOutlineViewDelegate

```swift
// Cell view for item
func outlineView(_ outlineView: NSOutlineView, viewFor tableColumn: NSTableColumn?, item: Any) -> NSView? {
    guard let sidebarItem = item as? SidebarItem else { return nil }

    if sidebarItem.isGroup {
        // Section header
        let cell = outlineView.makeView(
            withIdentifier: .init("HeaderCell"), owner: self
        ) as? NSTableCellView ?? NSTableCellView()
        cell.textField?.stringValue = sidebarItem.title.uppercased()
        cell.textField?.font = .systemFont(ofSize: 11, weight: .semibold)
        cell.textField?.textColor = .secondaryLabelColor
        return cell
    }

    // Regular row
    let cell = outlineView.makeView(
        withIdentifier: .init("DataCell"), owner: self
    ) as? NSTableCellView ?? NSTableCellView()

    let textField = cell.textField ?? NSTextField(labelWithString: "")
    textField.stringValue = sidebarItem.title

    let imageView = cell.imageView ?? NSImageView()
    if !sidebarItem.icon.isEmpty {
        imageView.image = NSImage(systemSymbolName: sidebarItem.icon, accessibilityDescription: nil)
    }

    if cell.textField == nil {
        cell.textField = textField
        cell.addSubview(textField)
    }
    if cell.imageView == nil {
        cell.imageView = imageView
        cell.addSubview(imageView)
    }

    return cell
}

// Row appearance
func outlineView(_ outlineView: NSOutlineView, isGroupItem item: Any) -> Bool {
    (item as? SidebarItem)?.isGroup ?? false
}

// Should select
func outlineView(_ outlineView: NSOutlineView, shouldSelectItem item: Any) -> Bool {
    !((item as? SidebarItem)?.isGroup ?? false)
}
```

## Selection Handling

```swift
func outlineViewSelectionDidChange(_ notification: Notification) {
    let row = outlineView.selectedRow
    guard row >= 0 else { return }
    guard let item = outlineView.item(atRow: row) as? SidebarItem else { return }

    // Notify other parts of the app
    NotificationCenter.default.post(
        name: .sidebarSelectionChanged,
        object: item
    )
}

// Programmatic selection
func select(item: SidebarItem) {
    let row = outlineView.row(forItem: item)
    if row >= 0 {
        outlineView.selectRowIndexes(IndexSet(integer: row), byExtendingSelection: false)
    }
}
```

## Drag and Drop

```swift
// Register for drag types
outlineView.registerForDraggedTypes([.string])
outlineView.setDraggingSourceOperationMask(.move, forLocal: true)

// Write dragged items
func outlineView(_ outlineView: NSOutlineView, pasteboardWriterForItem item: Any) -> (any NSPasteboardWriting)? {
    guard let sidebarItem = item as? SidebarItem else { return nil }
    return sidebarItem.id as NSString
}

// Validate drop
func outlineView(_ outlineView: NSOutlineView,
                 validateDrop info: any NSDraggingInfo,
                 proposedItem item: Any?,
                 proposedChildIndex index: Int) -> NSDragOperation {
    return .move
}

// Accept drop
func outlineView(_ outlineView: NSOutlineView,
                 acceptDrop info: any NSDraggingInfo,
                 item: Any?,
                 childIndex index: Int) -> Bool {
    // Reorder logic here
    outlineView.reloadData()
    return true
}
```

## Expand / Collapse

```swift
// Expand specific items
outlineView.expandItem(item)
outlineView.expandItem(item, expandChildren: true)  // Recursive

// Collapse
outlineView.collapseItem(item)

// Expand all root items on load
override func viewDidAppear() {
    super.viewDidAppear()
    for item in rootItems where !item.children.isEmpty {
        outlineView.expandItem(item)
    }
}
```

## Reload

```swift
outlineView.reloadData()                    // Full reload
outlineView.reloadItem(item)                // Single item
outlineView.reloadItem(item, reloadChildren: true)  // Item + children

// Animated insert/remove
outlineView.beginUpdates()
outlineView.insertItems(at: IndexSet(integer: 0), inParent: parent, withAnimation: .slideDown)
outlineView.removeItems(at: IndexSet(integer: 2), inParent: parent, withAnimation: .slideUp)
outlineView.endUpdates()
```
