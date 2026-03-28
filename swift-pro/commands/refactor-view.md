---
description: Extract and refactor SwiftUI views
allowed-tools: Read, Write, Edit, Grep, Glob
argument-hint: "<ViewFile.swift> - view file to refactor"
---

# Refactor SwiftUI View

Analyze a SwiftUI view file, extract long body sections into subviews and computed properties, and ensure correct state propagation.

## Step 1: Read the View File

Read the file provided as argument. Analyze:

1. **Body length** -- count lines in the `body` computed property
2. **Nesting depth** -- identify deeply nested view hierarchies (3+ levels)
3. **Repeated patterns** -- find duplicated view code
4. **Inline logic** -- find conditionals, loops, or formatting in the body
5. **State usage** -- map which `@State`, `@Binding`, `@Bindable`, `@Environment` properties exist and where they are used

## Step 2: Identify Extraction Targets

Flag sections that should be extracted:

### Extract to Computed Property when:
- A section is 10+ lines but does NOT need its own state or bindings
- A section is a logical unit (header, footer, toolbar content)
- The section only reads from the viewmodel (no write bindings)

### Extract to Subview (private struct) when:
- A section is 30+ lines
- A section manages its own local state
- A section could be reused elsewhere
- A section has a clear input/output boundary

### Extract to Separate File when:
- A component is genuinely reusable across features
- A component exceeds 50 lines with its own logic

## Step 3: Plan the Refactor

Before making changes, present the plan:

```
Refactor Plan: <FileName>
━━━━━━━━━━━━━━━━━━━━━━━━

Current body: XX lines
Target body:  XX lines

Extractions:
1. Lines XX-YY -> private var headerSection: some View
   Reason: logical grouping, read-only state access
2. Lines XX-YY -> private struct <Name>Row: View
   Reason: 30+ lines, takes binding to item
3. Lines XX-YY -> private var emptyState: some View
   Reason: self-contained, no bindings needed
```

## Step 4: Apply the Refactor

For each extraction:

### Computed Property Pattern
```swift
// MARK: - Sections

private var headerSection: some View {
    VStack {
        // extracted content
    }
}
```

### Subview with State Propagation
When the subview needs to write to parent state:

```swift
private struct ItemRow: View {
    @Bindable var viewModel: SomeViewModel  // for @Observable objects
    let item: Item

    var body: some View {
        // extracted content that can write to viewModel
    }
}
```

### State Propagation Rules

| Parent has | Child needs to read | Child needs to write | Pass as |
|-----------|--------------------|--------------------|---------|
| `@State var x: T` | yes | no | `let x: T` |
| `@State var x: T` | yes | yes | `@Binding var x: T` |
| `@State var vm: ViewModel` | yes (properties) | no | `let vm: ViewModel` |
| `@State var vm: ViewModel` | yes | yes (methods/properties) | `@Bindable var vm: ViewModel` |
| `@Environment(\.x)` | yes | no | `@Environment(\.x)` or pass as parameter |

**Critical:** When passing an `@Observable` object to a subview that calls mutating methods or binds to its properties, use `@Bindable` -- NOT `@Binding`, NOT `@ObservedObject`.

## Step 5: Verify No Functionality Changed

After refactoring, check:

1. **All state is still connected** -- search for every `viewModel.` reference in the original and verify it exists in the refactored version
2. **No dead code** -- all extracted sections are called from body
3. **Preview still works** -- the `#Preview` block compiles
4. **Modifiers preserved** -- `.onTapGesture`, `.sheet`, `.alert`, `.task` etc. are all still attached to the correct views

Search the modified file for potential issues:

```
# Verify all state properties are still used
grep -n "@State\|@Binding\|@Bindable\|@Environment" <file>

# Verify no orphaned modifiers
grep -n "\.sheet\|\.alert\|\.confirmationDialog\|\.fullScreenCover\|\.task\|\.onAppear" <file>
```

## Report

```
Refactored: <FileName>
━━━━━━━━━━━━━━━━━━━━━

Body: XX lines -> YY lines (ZZ% reduction)

Extractions:
  - headerSection (computed property, XX lines)
  - ItemRow (private subview, XX lines, @Bindable viewModel)
  - emptyState (computed property, XX lines)

State propagation:
  - viewModel passed as @Bindable to ItemRow (writes to .selectedItem)
  - All @Environment values preserved

Verification:
  - All state references accounted for
  - All modifiers preserved
  - Preview compiles
```
