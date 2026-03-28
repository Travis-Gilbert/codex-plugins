# PRD-Driven Development Workflow

## The 4-Phase Workflow

```
Phase 1: PRD          Phase 2: Spec         Phase 3: Tasks        Phase 4: Implement
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ What & Why   │ ---> │ How          │ ---> │ Work Units   │ ---> │ Code & Test  │
│              │      │              │      │              │      │              │
│ Problem      │      │ Architecture │      │ Ordered list │      │ Pick task    │
│ Users        │      │ Data models  │      │ Acceptance   │      │ Implement    │
│ Goals        │      │ API surface  │      │ criteria per │      │ Test         │
│ Constraints  │      │ UI flows     │      │ task         │      │ Build (MCP)  │
│ Non-goals    │      │ Tech choices │      │              │      │ Mark done    │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

Each phase produces a document that feeds the next. The PRD is owned by the product role (human or AI), the spec by engineering, tasks are derived mechanically, and implementation follows the task list.

---

## Phase 1: PRD (Product Requirements Document)

The PRD answers WHAT we are building and WHY. It deliberately avoids HOW.

### PRD Template

```markdown
# PRD: [Feature Name]

## Problem Statement
[1-3 paragraphs. What pain exists today? What opportunity are we pursuing?
Include data or user feedback if available.]

## Target Users
| Persona | Description | Primary Need |
|---------|-------------|--------------|
| [Name]  | [Who]       | [What]       |

## Goals
1. [Measurable outcome the feature should achieve]
2. [Another measurable outcome]
3. [...]

## Non-Goals
- [Explicitly out of scope for this iteration]
- [Things that might seem related but we are NOT doing]

## User Stories
- As a [persona], I want to [action] so that [benefit]
- As a [persona], I want to [action] so that [benefit]

## Constraints
- Platform: [iOS 17+, macOS 14+, etc.]
- Timeline: [Target date or sprint]
- Dependencies: [Backend API, third-party SDK, etc.]
- Performance: [Max latency, memory budget, etc.]

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| [What] | [Now]   | [Goal] |

## Open Questions
- [ ] [Unresolved decision that blocks spec work]
- [ ] [Another question]
```

### PRD Principles

- Keep it short (1-2 pages max)
- Use concrete examples over abstract descriptions
- Every goal must be testable / measurable
- Non-goals prevent scope creep -- list anything someone might assume is included
- Open questions MUST be resolved before moving to spec

---

## Phase 2: Feature Spec

The spec answers HOW we will build it. It translates PRD requirements into technical decisions.

### Feature Spec Template

```markdown
# Spec: [Feature Name]
PRD: [link or reference]

## Overview
[1 paragraph summary of the technical approach]

## Architecture

### Data Models
[SwiftData @Model classes, structs, enums]

```swift
@Model
class Workout {
    var name: String
    var exercises: [Exercise]
    var startedAt: Date
    var completedAt: Date?
    // ...
}
```

### API Contracts
[Endpoint definitions, request/response shapes]

```swift
enum WorkoutEndpoint: Endpoint {
    case list(page: Int)
    case detail(id: UUID)
    case create(CreateWorkoutRequest)
    case complete(id: UUID, CompletionData)
}
```

### View Hierarchy

```
WorkoutTab
├── WorkoutListView (NavigationStack root)
│   ├── WorkoutRow
│   └── EmptyStateView
├── WorkoutDetailView
│   ├── ExerciseSection
│   │   └── ExerciseRow
│   └── WorkoutSummaryCard
├── NewWorkoutSheet
│   └── ExercisePickerView
└── WorkoutHistoryView
```

### State Management
[ViewModels, shared state, data flow]

```swift
@Observable
class WorkoutListViewModel {
    var workouts: [Workout] = []
    var isLoading = false
    // ...
}
```

### Navigation
[Routes, deep links, sheet presentation]

```swift
enum WorkoutRoute: Hashable {
    case detail(Workout)
    case history
    case newWorkout
}
```

## Technical Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Persistence | SwiftData | Fits data model, CloudKit sync needed |
| Navigation | NavigationStack + Router | Supports deep linking requirement |
| Networking | Actor-based APIClient | Existing pattern in codebase |

## UI Wireframes
[ASCII diagrams or references to design files]

```
┌─────────────────────────┐
│ ← Workouts        [+]  │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ Morning Run    45m  │ │
│ │ Today, 7:00 AM      │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ Strength     1h 15m │ │
│ │ Yesterday, 6:00 PM  │ │
│ └─────────────────────┘ │
│                         │
│                         │
└─────────────────────────┘
```

## Edge Cases
- [ ] Offline: queue mutations, sync on reconnect
- [ ] Empty state: show onboarding prompt
- [ ] Large datasets: paginate at 50 items

## Security Considerations
- [Auth requirements, data sensitivity, etc.]

## Testing Strategy
- Unit: ViewModels, Services, Models
- Integration: API client with mock server
- UI: Core user flows (create, complete, delete)
```

### Spec Review Checklist

Before moving to tasks, verify:
- [ ] Every PRD goal maps to at least one spec section
- [ ] Every PRD non-goal is NOT addressed in the spec
- [ ] Data models cover all user stories
- [ ] API contracts match backend team's agreement
- [ ] Edge cases are listed with handling strategy
- [ ] No ambiguity in the view hierarchy

---

## Phase 3: Task Generation

Break the spec into ordered, implementable tasks. Each task should be completable in one session (1-4 hours).

### Task Template

```markdown
## Tasks: [Feature Name]
Spec: [link or reference]

### Task 1: Data Models
**Files:** `Models/Workout.swift`, `Models/Exercise.swift`
**Acceptance Criteria:**
- [ ] @Model class Workout with all spec properties
- [ ] @Model class Exercise with relationship to Workout
- [ ] #Unique constraint on Workout.id
- [ ] Unit tests for model creation and relationships
**Depends on:** Nothing
**Estimate:** 1 hour

### Task 2: Repository Layer
**Files:** `Services/WorkoutRepository.swift`
**Acceptance Criteria:**
- [ ] Protocol: WorkoutRepositoryProtocol
- [ ] CRUD operations using ModelContext
- [ ] Fetch with filtering and sorting
- [ ] Unit tests with in-memory ModelContainer
**Depends on:** Task 1
**Estimate:** 1.5 hours

### Task 3: API Client Endpoints
**Files:** `Networking/WorkoutEndpoint.swift`
**Acceptance Criteria:**
- [ ] All endpoints from spec implemented
- [ ] Request/response DTOs with Codable
- [ ] Unit tests for endpoint URL construction
**Depends on:** Nothing
**Estimate:** 1 hour

### Task 4: WorkoutListViewModel
**Files:** `ViewModels/WorkoutListViewModel.swift`
**Acceptance Criteria:**
- [ ] @Observable class with all state from spec
- [ ] Load, create, delete actions
- [ ] Error handling with AppError
- [ ] Unit tests (mock repository)
**Depends on:** Task 2
**Estimate:** 2 hours

### Task 5: WorkoutListView
**Files:** `Views/Workouts/WorkoutListView.swift`, `Views/Workouts/WorkoutRow.swift`
**Acceptance Criteria:**
- [ ] NavigationStack with list
- [ ] Empty state with ContentUnavailableView
- [ ] Pull to refresh
- [ ] Swipe to delete
- [ ] Preview with sample data
**Depends on:** Task 4
**Estimate:** 2 hours

### Task 6: Navigation and Routing
**Files:** `Navigation/WorkoutRoute.swift`, `Navigation/Router+Workout.swift`
**Acceptance Criteria:**
- [ ] WorkoutRoute enum
- [ ] Router handles deep link: myapp://workout/{id}
- [ ] Sheet presentation for NewWorkout
**Depends on:** Task 5
**Estimate:** 1 hour
```

### Task Ordering Rules

1. Data models and protocols first (no dependencies)
2. Service/repository layer next (depends on models)
3. ViewModels (depends on services)
4. Views (depends on ViewModels)
5. Navigation and integration last

Tasks with no dependencies can be parallelized.

### Task Sizing

| Size | Duration | Complexity |
|------|----------|------------|
| Small | < 1 hour | Single file, clear implementation |
| Medium | 1-2 hours | 2-3 files, some design decisions |
| Large | 2-4 hours | Multiple files, edge cases |
| Too Large | > 4 hours | Split into smaller tasks |

---

## Phase 4: Implementation Workflow

### Per-Task Cycle

```
1. Pick next unblocked task
       │
       ▼
2. Read task acceptance criteria
       │
       ▼
3. Implement (code + tests)
       │
       ▼
4. Build via XcodeBuildMCP
       │
       ├── Build fails → Fix errors → Rebuild
       │
       ▼
5. Run tests via XcodeBuildMCP
       │
       ├── Tests fail → Fix → Rerun
       │
       ▼
6. Verify all acceptance criteria
       │
       ├── Not met → Continue implementing
       │
       ▼
7. Mark task complete ✓
       │
       ▼
8. Pick next task (back to 1)
```

### Implementation Checklist Per Task

```markdown
- [ ] Read acceptance criteria
- [ ] Create/modify files listed in task
- [ ] Write tests FIRST (or alongside)
- [ ] Build passes (`build_sim_name_proj`)
- [ ] Tests pass (`test_sim_name_proj` or `swift_package_test`)
- [ ] All acceptance criteria checked off
- [ ] No warnings introduced
- [ ] Code follows project conventions
```

### Build-Test Cycle Commands

```
1. discover_projects           → Find the .xcodeproj/.xcworkspace
2. build_sim_name_proj         → Build for simulator
3. test_sim_name_proj          → Run tests on simulator
4. (if app) boot_simulator     → Start a simulator
5. (if app) install_app        → Install the built app
6. (if app) launch_app         → Launch for manual/screenshot verification
7. (if app) screenshot         → Capture current state
```

### Error Diagnosis Loop

When a build or test fails:
1. Read the error output carefully
2. Identify the root cause (compiler error, runtime crash, assertion failure)
3. Fix the specific issue
4. Rebuild/retest
5. If the same error persists, re-read the relevant spec section

Do NOT:
- Fix errors by commenting out code
- Skip failing tests
- Change acceptance criteria to match broken implementation

---

## Tracking Progress

### Status Table

Maintain in CLAUDE.md or a tracking document:

```markdown
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Data Models | Done | |
| 2 | Repository Layer | Done | |
| 3 | API Endpoints | Done | |
| 4 | WorkoutListViewModel | In Progress | Error handling remaining |
| 5 | WorkoutListView | Blocked | Waiting on Task 4 |
| 6 | Navigation | Not Started | |
```

### Status Values

| Status | Meaning |
|--------|---------|
| Not Started | Task has not been picked up |
| In Progress | Currently being implemented |
| Blocked | Depends on incomplete task or unresolved question |
| Done | All acceptance criteria met, tests pass |
| Revised | Spec changed, task needs re-evaluation |

---

## When to Revise

Go back to an earlier phase when:

| Signal | Action |
|--------|--------|
| Implementation reveals spec gap | Update spec, regenerate affected tasks |
| User feedback changes requirements | Update PRD, cascade through spec and tasks |
| Technical constraint discovered | Update spec's technical decisions, adjust tasks |
| Task is consistently > 4 hours | Split the task, update task list |
| Multiple tasks have the same blocker | Address the blocker as a new task inserted before them |
