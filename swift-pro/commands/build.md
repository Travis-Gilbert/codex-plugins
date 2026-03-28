---
description: Build the project via XcodeBuildMCP
allowed-tools: Bash, Read, Grep, Glob
---

# Build Project

Build the current Xcode project using XcodeBuildMCP tooling.

## Step 1: Discover the Project

Search the working directory for the Xcode project or workspace.

```bash
# Find .xcworkspace first (preferred), then .xcodeproj
find . -maxdepth 3 -name "*.xcworkspace" -not -path "*/Pods/*" -not -path "*/.build/*" | head -5
find . -maxdepth 3 -name "*.xcodeproj" | head -5
```

If both exist, prefer the `.xcworkspace`. If a Package.swift exists at root, this is a Swift Package -- use `swift build` instead.

## Step 2: Identify Scheme and Target

```bash
# List available schemes
xcodebuild -list -workspace <Workspace>.xcworkspace 2>/dev/null || xcodebuild -list -project <Project>.xcodeproj
```

Choose the main app scheme (not test or UI test schemes). If multiple schemes exist, pick the one matching the project name.

## Step 3: Build

Run `build_sim_name_proj` via XcodeBuildMCP to build the project for the simulator. If XcodeBuildMCP tools are not available, fall back to xcodebuild:

```bash
xcodebuild build \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -quiet 2>&1
```

## Step 4: Parse Build Results

Examine the output for errors and warnings.

### If the build succeeds:
Report: "Build succeeded" with the scheme name, target platform, and any warnings.

### If the build fails:
Categorize each error:

| Category | Examples | Suggested Fix |
|----------|----------|---------------|
| Missing import | `No such module 'X'` | Check Package.swift or Podfile for dependency |
| Type error | `Cannot convert value of type X to Y` | Show the offending line and suggest the correct type |
| Missing member | `Value of type X has no member Y` | Check API changes, suggest correct property/method name |
| Syntax error | `Expected X` | Show the line and indicate the syntax issue |
| Concurrency | `Sending X risks causing data races` | Suggest `@Sendable`, `@MainActor`, or actor isolation fix |
| Linker error | `Undefined symbol` | Check target membership and linked frameworks |

For each error:
1. Show the file path and line number
2. Show the error message
3. Suggest a specific fix

Present a summary table of all errors grouped by category.
