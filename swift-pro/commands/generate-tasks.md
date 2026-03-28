---
description: Break a spec into implementable tasks
allowed-tools: Read, Write, Grep, Glob
argument-hint: "<spec-file> - path to feature spec"
---

# Generate Tasks

Read a technical specification and break it into ordered, implementable tasks with acceptance criteria.

## Step 1: Read the Spec

Read the spec file provided as argument. Identify all implementation work:
- Data models to create
- Services and data layer
- ViewModels
- Views and UI components
- Tests
- Integration points (navigation, dependency wiring)

## Step 2: Analyze Dependencies

Scan the codebase to understand:

```bash
# Check for existing patterns this feature will follow
find . -name "*.swift" -path "*/Models/*" -not -path "*/.build/*" | head -10
find . -name "*.swift" -path "*/ViewModels/*" -not -path "*/.build/*" | head -10
find . -name "*.swift" -path "*/Services/*" -not -path "*/.build/*" | head -10
```

Identify which tasks depend on others to determine ordering.

## Step 3: Generate Task List

Write a task document with numbered, ordered tasks:

```markdown
# Tasks: <Feature Name>

**Spec:** <path to spec>
**Date:** <today>
**Estimated total:** <S/M/L>

## Task Dependency Graph

```
T1 (Model) ──> T2 (Service) ──> T3 (ViewModel) ──> T4 (View)
                                       |
                                       v
                                  T5 (Tests)
```

## Tasks

### T1: Create <Model> data model
**Complexity:** S
**Dependencies:** None
**Files:** `<path>/Models/<Model>.swift`

Create the `<Model>` struct with:
- [ ] Properties: <list from spec>
- [ ] Conformances: Identifiable, Codable, Hashable, Sendable
- [ ] Initializer with sensible defaults

**Acceptance criteria:**
- Model compiles with all required properties
- Conforms to Identifiable, Codable, Hashable, Sendable
- Includes Codable coding keys if API field names differ

---

### T2: Create <Service> data layer
**Complexity:** M
**Dependencies:** T1
**Files:** `<path>/Services/<Service>.swift`

- [ ] Define protocol for testability
- [ ] Implement concrete class
- [ ] Handle error cases from spec
- [ ] Add async/await API

**Acceptance criteria:**
- Protocol defined with async methods
- Concrete implementation handles all error cases
- Errors are typed (enum, not generic Error)

---

### T3: Create <FeatureName>ViewModel
**Complexity:** M
**Dependencies:** T1, T2
**Files:** `<path>/ViewModels/<FeatureName>ViewModel.swift`

- [ ] @Observable class with state from spec
- [ ] Actions for each user interaction
- [ ] Error handling and loading states
- [ ] Integration with service layer

**Acceptance criteria:**
- All state properties from spec present
- All actions from spec implemented
- Loading and error states handled
- Uses @Observable, not ObservableObject

---

### T4: Build <FeatureName>View
**Complexity:** M
**Dependencies:** T3
**Files:** `<path>/Views/<FeatureName>View.swift`

- [ ] Main view with @State viewModel
- [ ] Loading state (ProgressView)
- [ ] Empty state (ContentUnavailableView)
- [ ] Error state (error banner or alert)
- [ ] Populated state (main content)
- [ ] Navigation and toolbar
- [ ] #Preview

**Acceptance criteria:**
- All four states render correctly
- Navigation works as specified
- Uses @State (not @StateObject)
- Preview compiles and renders

---

### T5: Write tests
**Complexity:** M
**Dependencies:** T3
**Files:** `<test-path>/<FeatureName>ViewModelTests.swift`

- [ ] Initial state tests
- [ ] Action tests (one per action)
- [ ] Error handling tests
- [ ] Edge case tests from spec

**Acceptance criteria:**
- Every ViewModel action has at least one test
- Error paths tested
- Edge cases from spec covered
- All tests pass

---

### T6: Integration
**Complexity:** S
**Dependencies:** T4
**Files:** <navigation file>, <app entry point>

- [ ] Register view in app navigation
- [ ] Add to tab bar / sidebar if applicable
- [ ] Wire up any dependency injection

**Acceptance criteria:**
- Feature accessible from main navigation
- Build succeeds
- All tests pass
```

Adjust complexity estimates:
- **S (Small):** < 1 hour, single file, straightforward
- **M (Medium):** 1-3 hours, 2-4 files, some design decisions
- **L (Large):** 3+ hours, 5+ files, complex logic or significant UI

## Step 4: Save the Tasks

Derive the feature name from the spec filename (e.g., `spec-user-profile.md` becomes `tasks-user-profile.md`).

Save to: `docs/tasks-<feature-name>.md`

## Step 5: Present Summary

Tell the user:
- Where the task file was saved
- Total number of tasks
- Estimated overall complexity
- Recommended implementation order
- Suggest running `/implement-feature docs/spec-<feature-name>.md` to begin implementation
