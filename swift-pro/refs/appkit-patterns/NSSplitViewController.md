# NSSplitViewController Reference

## Basic 3-Pane Layout

```swift
final class MainSplitVC: NSSplitViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let sidebar = NSSplitViewItem(sidebarWithViewController: SidebarVC())
        sidebar.canCollapse = true
        sidebar.minimumThickness = 200
        sidebar.maximumThickness = 300

        let content = NSSplitViewItem(contentListWithViewController: ContentListVC())
        content.minimumThickness = 250

        let detail = NSSplitViewItem(viewController: DetailVC())
        detail.minimumThickness = 400

        addSplitViewItem(sidebar)
        addSplitViewItem(content)
        addSplitViewItem(detail)

        splitView.autosaveName = "MainSplitView"
    }
}
```

## Factory Methods

| Method | Purpose | Visual Style |
|--------|---------|-------------|
| `sidebarWithViewController(_:)` | Source list sidebar | Vibrant background, sidebar width behavior |
| `contentListWithViewController(_:)` | Middle content pane | Standard background |
| `NSSplitViewItem(viewController:)` | Generic pane | No special styling |
| `inspectorWithViewController(_:)` | Right inspector | Inspector-width defaults |

## Collapsible Panes

```swift
// Make sidebar collapsible
sidebarItem.canCollapse = true
sidebarItem.isCollapsed = false  // Initial state

// Toggle sidebar programmatically
func toggleSidebar() {
    guard let sidebar = splitViewItems.first else { return }
    NSAnimationContext.runAnimationGroup { context in
        context.duration = 0.25
        sidebar.animator().isCollapsed.toggle()
    }
}

// Respond to .toggleSidebar action (toolbar button, menu item)
// NSSplitViewController already handles this with the standard
// NSToolbarItem(itemIdentifier: .toggleSidebar)
```

## Autosave

```swift
// Persist split positions across launches
splitView.autosaveName = "MainSplit"

// Each NSSplitViewItem's holding priority affects resize behavior:
sidebarItem.holdingPriority = .defaultLow + 1
contentItem.holdingPriority = .defaultLow + 2
detailItem.holdingPriority = .defaultLow      // Resizes first
```

## Minimum / Maximum Widths

```swift
item.minimumThickness = 200   // CGFloat
item.maximumThickness = 400   // CGFloat — use .greatestFiniteMagnitude for no max

// Or constrain via Auto Layout in the child view controller:
view.widthAnchor.constraint(greaterThanOrEqualToConstant: 200).isActive = true
```

## Delegate Methods

```swift
extension MainSplitVC: NSSplitViewDelegate {
    // Control minimum sizes
    func splitView(_ splitView: NSSplitView,
                   constrainMinCoordinate proposedMinimumPosition: CGFloat,
                   ofSubviewAt dividerIndex: Int) -> CGFloat {
        return max(proposedMinimumPosition, 200)
    }

    // React to resize
    func splitViewDidResizeSubviews(_ notification: Notification) {
        // Update layout or save state
    }

    // Control which dividers can be dragged
    func splitView(_ splitView: NSSplitView,
                   shouldAdjustSizeOfSubview view: NSView) -> Bool {
        return true
    }
}
```

## Holding Priority

Controls which pane resizes when the window resizes:
- Lower priority = resizes first
- Higher priority = resizes last (holds its size)

```swift
sidebarItem.holdingPriority = .init(251)   // Holds
contentItem.holdingPriority = .init(250)   // Resizes before sidebar
detailItem.holdingPriority = .init(249)    // Resizes first
```

## Vertical Split

```swift
splitView.isVertical = false  // Horizontal split (top/bottom)
splitView.isVertical = true   // Vertical split (left/right) — default
```

## Common Patterns

- Use `sidebarWithViewController` for the left pane to get correct vibrancy.
- Set `autosaveName` on the split view so pane widths persist.
- Use `NSToolbarItem(itemIdentifier: .toggleSidebar)` for the standard sidebar toggle.
- Collapse inspector panes from the right, sidebar from the left.
- Access child VCs: `splitViewItems[0].viewController`.
