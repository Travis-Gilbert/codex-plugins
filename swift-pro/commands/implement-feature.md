---
description: Implement a feature from spec with tests
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "<spec-file> - path to feature spec"
---

# Implement Feature from Spec

Read a feature specification and implement it with full test coverage.

## Step 1: Read the Spec

Read the spec file provided as argument. Extract:

- **Data models** -- entities, properties, relationships
- **Views** -- screens, navigation flow, UI components
- **State management** -- what state exists, how it changes
- **Business logic** -- rules, validations, transformations
- **Edge cases** -- error states, empty states, loading states
- **API contracts** -- endpoints, request/response shapes (if applicable)

If the spec is ambiguous on any point, list assumptions before proceeding.

## Step 2: Create Implementation Plan

Before writing code, produce a numbered plan:

```
Implementation Plan: <Feature Name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Models
   - [ ] <Model> struct with properties X, Y, Z
   - [ ] <Model> conformance to Codable, Identifiable

2. Services / Data Layer
   - [ ] <Service> for data fetching / persistence
   - [ ] Error types

3. ViewModels
   - [ ] <ViewModel> with state and actions

4. Views
   - [ ] <View> -- main screen
   - [ ] <SubView> -- extracted component

5. Tests
   - [ ] <ViewModel>Tests
   - [ ] <Model>Tests (if non-trivial logic)

6. Integration
   - [ ] Register in navigation
   - [ ] Add to tab bar / sidebar if needed
```

## Step 3: Implement Each Component

Work through the plan in order. For each component:

1. **Write the code** following project conventions
2. **Use modern Swift patterns**:
   - `@Observable` (not `ObservableObject`)
   - `@State` (not `@StateObject`)
   - `async/await` (not completion handlers)
   - Swift Testing (not XCTest, unless the project uses XCTest)
   - `#Preview` (not `PreviewProvider`)
3. **Handle all states**: loading, empty, error, populated
4. **Add accessibility**: labels, traits, hints where appropriate

## Step 4: Write Tests

For each ViewModel and any model with business logic:

```swift
import Testing
@testable import <ModuleName>

struct <Component>Tests {
    // Test initial state
    // Test each action
    // Test error handling
    // Test edge cases from the spec
}
```

Aim for:
- Every public method tested
- Every state transition tested
- Every error path tested
- Edge cases from the spec covered

## Step 5: Build

```bash
xcodebuild build \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -quiet 2>&1
```

Fix any build errors before proceeding.

## Step 6: Run Tests

```bash
xcodebuild test \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  2>&1
```

Fix any test failures.

## Report

```
Feature Implemented: <Feature Name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files created/modified:
  <list of files>

Test coverage:
  <N> test cases across <M> test suites
  All passing

Spec items addressed:
  - [x] <item from spec>
  - [x] <item from spec>

Notes:
  - <any assumptions made>
  - <any deviations from spec with rationale>
```
