---
description: Plan-mode feature analysis using Opus
allowed-tools: Read, Grep, Glob
argument-hint: "<feature-description> - what to analyze"
---

# Plan Feature

Analyze the codebase and produce a structured feature plan. This is a planning-only command -- it produces analysis and recommendations, not code.

## Step 1: Understand the Request

Parse the feature description from the argument. Identify:
- What the feature does from the user's perspective
- Which parts of the app it touches
- Whether it is a new feature, extension of existing, or refactor

## Step 2: Analyze the Codebase

Search for relevant patterns and existing code.

### Architecture Scan

```
# Project structure
find . -type d -maxdepth 3 -not -path "*/.build/*" -not -path "*/Pods/*" -not -path "*/.git/*"

# Navigation pattern
grep -r "NavigationStack\|NavigationSplitView\|TabView\|NavigationLink" --include="*.swift" -l
grep -r "Coordinator\|Router\|FlowController" --include="*.swift" -l

# State management
grep -r "@Observable\|ObservableObject\|@EnvironmentObject\|@Environment" --include="*.swift" -l

# Data persistence
grep -r "SwiftData\|CoreData\|@Model\|NSManagedObject\|UserDefaults\|Keychain" --include="*.swift" -l

# Networking
grep -r "URLSession\|Alamofire\|Moya\|async.*throws.*->.*Decodable" --include="*.swift" -l
```

### Relevant Code

Search for code directly related to the feature:
- Models that will be affected
- Views that will change or be extended
- Services or managers involved
- Existing tests in the affected area

Read key files to understand their structure.

## Step 3: Identify Architectural Impact

Assess what this feature changes:

| Area | Impact | Details |
|------|--------|---------|
| Models | New / Modified / None | What data structures change |
| Views | New / Modified / None | What screens are added or changed |
| Navigation | New / Modified / None | New routes or flow changes |
| Persistence | New / Modified / None | Storage requirements |
| Networking | New / Modified / None | API calls needed |
| Tests | New / Modified / None | Test coverage needed |

## Step 4: Propose Approach

Present 1-2 approaches (if there are meaningful alternatives):

### Approach A: <Name>

**Summary:** <1-2 sentences>

**Pros:**
- <advantage>
- <advantage>

**Cons:**
- <disadvantage>
- <disadvantage>

**Files affected:**
- `<path>` -- <what changes>
- `<path>` -- <what changes>

### Approach B: <Name> (if applicable)

...

### Recommendation

State which approach to use and why.

## Step 5: Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| <risk> | Low/Med/High | Low/Med/High | <how to avoid> |

Common risks to evaluate:
- Breaking existing functionality
- Performance implications (large lists, complex layouts)
- Concurrency issues (actor isolation, Sendable conformance)
- State management complexity
- Migration concerns (data model changes)

## Step 6: Implementation Order

Suggest the order to implement:

```
1. <Component> -- <why first>
2. <Component> -- <depends on 1>
3. <Component> -- <depends on 2>
...
```

## Output Format

Present the entire analysis as structured text. Do NOT write any code files. The output should help the user (or a subsequent `/implement-feature` run) understand exactly what to build, where, and in what order.
