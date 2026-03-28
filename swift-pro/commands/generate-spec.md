---
description: Generate a feature spec from a PRD
allowed-tools: Read, Write, Grep, Glob
argument-hint: "<prd-file> - path to PRD"
---

# Generate Feature Spec

Read a PRD and generate a detailed technical specification for implementation.

## Step 1: Read the PRD

Read the PRD file provided as argument. Extract:
- Problem statement and goals
- User stories and acceptance criteria
- Constraints and non-goals

## Step 2: Analyze the Codebase

Scan the project to understand existing patterns:

```bash
# Existing models and data layer
find . -name "*.swift" -not -path "*/.build/*" -not -path "*/Pods/*" | head -50
```

Search for:
- Existing data models that this feature will interact with
- Navigation patterns in use (NavigationStack, TabView, coordinator)
- Networking layer conventions (URLSession, Alamofire, custom)
- Persistence layer (SwiftData, Core Data, UserDefaults, custom)
- Dependency injection patterns

## Step 3: Generate the Spec

Write a technical specification with these sections:

```markdown
# Spec: <Feature Name>

**PRD:** <path to PRD>
**Date:** <today>

## Overview

<1-2 sentence technical summary.>

## Data Models

### <ModelName>

| Property | Type | Notes |
|----------|------|-------|
| id | UUID | Primary identifier |
| ... | ... | ... |

**Conformances:** Identifiable, Codable, Hashable, Sendable

**Relationships:**
- <describe relationships to other models>

## API Contracts (if applicable)

### <Endpoint>

- **Method:** GET/POST/PUT/DELETE
- **Path:** /api/v1/<resource>
- **Request:** <shape>
- **Response:** <shape>
- **Error cases:** <list>

## View Hierarchy

```
<FeatureName>View (NavigationStack)
  +-- <ListSection>
  |     +-- <RowView>
  +-- <DetailView>
  |     +-- <SubComponent>
  +-- <FormView> (sheet)
```

## State Management

### <FeatureName>ViewModel (@Observable)

| Property | Type | Initial | Description |
|----------|------|---------|-------------|
| items | [<Model>] | [] | Loaded data |
| isLoading | Bool | false | Loading indicator |
| errorMessage | String? | nil | Error display |

### Actions

| Action | Trigger | Side Effects |
|--------|---------|-------------|
| onAppear() | .task | Loads items |
| add(_:) | Toolbar button | Appends to items |
| delete(at:) | Swipe to delete | Removes from items |

## Error Handling

| Error Case | User Experience | Recovery |
|------------|-----------------|----------|
| Network failure | Error banner with retry | Retry button |
| Invalid input | Inline validation | Highlight field |
| Empty state | ContentUnavailableView | CTA button |

## Edge Cases

- <edge case from PRD>
- <additional edge cases identified during analysis>

## Dependencies

- <existing modules this feature depends on>
- <new dependencies needed, if any>

## Out of Scope

- <items explicitly excluded per PRD non-goals>
```

## Step 4: Save the Spec

Derive the feature name from the PRD filename (e.g., `prd-user-profile.md` becomes `spec-user-profile.md`).

Save to: `docs/spec-<feature-name>.md`

## Step 5: Present Summary

Tell the user:
- Where the spec was saved
- Count of models, views, and API endpoints defined
- Any assumptions made beyond the PRD
- Suggest running `/generate-tasks docs/spec-<feature-name>.md` as the next step
