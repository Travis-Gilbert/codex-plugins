# Feature Spec: {Feature Name}

**PRD:** {Link or reference to PRD}
**Author:** {name}
**Date:** {date}
**Status:** Draft | In Review | Approved

---

## Overview

One-paragraph summary of what this feature does and how it fits into the app.

## Data Models

### SwiftData Models

```swift
@Model
final class {ModelName} {
    // Properties, relationships, indexes
}
```

### DTOs / API Response Types

```swift
struct {ModelName}Response: Codable {
    // Fields matching API contract
}
```

### Enums / Value Types

```swift
enum {TypeName}: String, Codable {
    // Cases
}
```

## API Contracts

| Method | Path | Auth | Request Body | Response | Notes |
|--------|------|------|-------------|----------|-------|
| GET | /v1/{resource} | Yes | -- | `[{Model}]` | Paginated |
| POST | /v1/{resource} | Yes | `Create{Model}Request` | `{Model}` | |
| PUT | /v1/{resource}/{id} | Yes | `Update{Model}Request` | `{Model}` | |
| DELETE | /v1/{resource}/{id} | Yes | -- | 204 | |

## View Hierarchy

```
NavigationStack
  {Feature}View
    HeaderSection
    ContentList
      ItemRow
        ItemDetail (navigation destination)
    EmptyState
    ErrorState
```

### Key Views

| View | Purpose | State Source |
|------|---------|-------------|
| `{Feature}View` | Root container | `@State viewModel` |
| `ItemRow` | List cell | Props from parent |
| `ItemDetail` | Detail push | `@Query` + ViewModel |

## State Management

### ViewModel

```
{Feature}ViewModel (@Observable)
  items: [{Model}]
  isLoading: Bool
  errorMessage: String?
  selectedFilter: Filter

  load() async
  refresh() async
  delete(item:) async
  applyFilter(_:)
```

### State Flow

```
View.task → ViewModel.load() → APIClient.request() → Update items
View.refreshable → ViewModel.refresh() → APIClient.request() → Update items
View.onDelete → ViewModel.delete() → APIClient.request() → Remove from items
```

## Error Handling

| Error | User-Facing Message | Recovery |
|-------|---------------------|----------|
| Network unavailable | "No internet connection." | Retry button |
| 401 Unauthorized | "Session expired." | Redirect to sign-in |
| 404 Not Found | "Item no longer exists." | Pop to list |
| Decoding failure | "Something went wrong." | Retry button + log |
| Unknown | "Something went wrong." | Retry button |

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Empty list | Show empty state illustration + CTA |
| Very long text | Truncate with `lineLimit`, full text in detail |
| Rapid taps | Debounce or disable button during request |
| Offline with cached data | Show cached data + offline banner |
| Concurrent edits | Last-write-wins or conflict resolution? |
| Deep link to deleted item | Show "Item not found" + navigate back |
