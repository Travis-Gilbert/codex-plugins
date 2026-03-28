---
description: Diagnose and fix build errors
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Fix Build Errors

Diagnose and fix all build errors in the project, one at a time.

## Step 1: Run the Build

Build the project and capture all errors:

```bash
xcodebuild build \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  2>&1
```

If the build succeeds with no errors, report "Build clean -- no errors to fix" and stop.

## Step 2: Collect and Classify Errors

Parse every error from the build output. Classify each one:

| Category | Pattern | Specialist Context |
|----------|---------|-------------------|
| Concurrency | `Sending X risks causing data races`, `non-sendable`, `actor-isolated`, `@MainActor` | Load concurrency-specialist agent context if available |
| SwiftUI | `Cannot convert value`, `Missing argument`, `Type X is not convertible to Y` in View bodies | Load swiftui-builder agent context if available |
| Missing dependency | `No such module` | Check Package.swift / Podfile |
| Type mismatch | `Cannot convert value of type`, `Cannot assign value of type` | Read the relevant type definitions |
| Missing member | `has no member`, `cannot find X in scope` | Check for API renames or typos |
| Protocol conformance | `does not conform to protocol` | Read the protocol definition and add missing requirements |
| Access control | `is inaccessible due to` | Adjust access level |
| Linker | `Undefined symbol`, `duplicate symbol` | Check target membership |

## Step 3: Fix Errors One at a Time

For each error, in order of dependency (fix foundational errors first):

1. **Read the file** at the error location with surrounding context (at least 10 lines above and below)
2. **Understand the intent** -- what was the code trying to do?
3. **Apply the fix** using the Edit tool
4. **Explain the fix** briefly

### Fix Priority Order:
1. Missing imports and dependencies (unblocks other errors)
2. Type definitions and protocol conformances (unblocks usage errors)
3. Type mismatches and missing members
4. Concurrency issues
5. Warnings promoted to errors

## Step 4: Rebuild After Each Fix

After fixing each error (or a batch of closely related errors in the same file):

```bash
xcodebuild build \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  2>&1
```

Check if new errors were introduced by the fix. If so, address them before moving on.

## Step 5: Report

When the build succeeds, present a summary:

```
Build Fixed
━━━━━━━━━━━
Errors fixed: N
Files modified: [list]

Changes:
1. <file>:<line> -- <what was fixed and why>
2. ...
```

If any errors remain unfixed (e.g., require user decision), list them with recommended approaches.
