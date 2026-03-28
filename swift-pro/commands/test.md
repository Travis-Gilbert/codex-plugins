---
description: Run tests via XcodeBuildMCP
allowed-tools: Bash, Read, Grep, Glob
argument-hint: "[test-name] - specific test to run, or blank for all"
---

# Run Tests

Run the project test suite using XcodeBuildMCP tooling.

## Step 1: Discover the Project

```bash
# Find project/workspace
find . -maxdepth 3 -name "*.xcworkspace" -not -path "*/Pods/*" -not -path "*/.build/*" | head -5
find . -maxdepth 3 -name "*.xcodeproj" | head -5
find . -maxdepth 1 -name "Package.swift" | head -1
```

## Step 2: Identify Test Target

```bash
xcodebuild -list -workspace <Workspace>.xcworkspace 2>/dev/null || xcodebuild -list -project <Project>.xcodeproj
```

Look for schemes ending in `Tests` or the main scheme (which typically includes test targets).

## Step 3: Run Tests

If a specific test name was provided as an argument, run only that test. Otherwise run the full suite.

Run `test_sim_name_proj` via XcodeBuildMCP. If XcodeBuildMCP tools are not available, fall back to xcodebuild:

**All tests:**
```bash
xcodebuild test \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -resultBundlePath TestResults.xcresult \
  2>&1
```

**Specific test:**
```bash
xcodebuild test \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:<TestTarget>/<TestClass>/<testMethodName> \
  2>&1
```

## Step 4: Parse Test Results

Extract from the output:
- Total tests run
- Tests passed
- Tests failed
- Tests skipped

### Report Format

```
Test Results: <Scheme>
━━━━━━━━━━━━━━━━━━━━
Passed: XX
Failed: XX
Skipped: XX
Total:  XX
```

### For each failed test:
1. Show the test class and method name
2. Show the assertion that failed with expected vs actual values
3. Show the file path and line number
4. If the failure message references a specific value, read the test file to understand context

### For skipped tests:
List them with the skip reason if available.

### If all tests pass:
Report the count and total execution time.
