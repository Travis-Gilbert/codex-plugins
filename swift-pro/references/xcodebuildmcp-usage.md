# XcodeBuildMCP Tool Usage Guide

## Overview

XcodeBuildMCP provides MCP tools for building, testing, running, and debugging Xcode projects and Swift packages without opening Xcode. These tools are the primary build-test interface during implementation.

---

## Tool Reference

### discover_projects

Finds Xcode projects, workspaces, and Swift packages in the working directory.

**When to use:** At the start of any implementation session to identify the project structure.

```
discover_projects
```

**Returns:** List of `.xcodeproj`, `.xcworkspace`, and `Package.swift` files with their paths, schemes, and targets.

**Typical output:**
```
Found projects:
- /path/to/MyApp.xcodeproj
  Schemes: MyApp, MyAppTests
  Targets: MyApp, MyAppKit, MyAppTests, MyAppUITests
- /path/to/Package.swift
  Targets: MyLibrary, MyLibraryTests
```

---

### build_sim_name_proj

Builds the project for a named simulator.

**When to use:** After making code changes, before running tests or installing the app.

```
build_sim_name_proj
  project: "MyApp.xcodeproj"    # or workspace
  scheme: "MyApp"
  simulator: "iPhone 16 Pro"    # simulator name
  configuration: "Debug"        # Debug or Release
```

**Common configurations:**
- `Debug` -- fast builds, includes debug symbols, assertions enabled
- `Release` -- optimized, strip symbols, for performance testing

**Build error patterns and fixes:**

| Error Pattern | Likely Cause | Fix |
|---------------|-------------|-----|
| `Cannot find type 'X' in scope` | Missing import or typo | Add `import` statement or check spelling |
| `Value of type 'X' has no member 'Y'` | Wrong type or outdated API | Check type definition, verify API availability |
| `Cannot convert value of type 'X' to expected 'Y'` | Type mismatch | Add explicit conversion or fix the type |
| `Missing argument for parameter 'X'` | Init/function signature changed | Add the missing parameter |
| `Ambiguous use of 'X'` | Multiple matching declarations | Qualify with module name: `MyModule.X` |
| `Circular reference` | Two types referencing each other | Use protocol or break cycle with optional |
| `Sendable closure captures mutable variable` | Concurrency safety | Make variable `let` or use actor |
| `Expression too complex` | Complex chain of operations | Break into intermediate variables |

---

### test_sim_name_proj

Runs tests for the project on a named simulator.

**When to use:** After a successful build, to verify all tests pass.

```
test_sim_name_proj
  project: "MyApp.xcodeproj"
  scheme: "MyAppTests"
  simulator: "iPhone 16 Pro"
  test_identifier: "UserServiceTests"  # optional: specific test suite
```

**Test result parsing:**

| Result | Meaning | Action |
|--------|---------|--------|
| `Test Suite 'X' passed` | All tests in suite passed | Continue |
| `Test Suite 'X' failed` | One or more tests failed | Read failure details |
| `X.testY(): XCTAssertEqual failed: ("A") is not equal to ("B")` | Assertion mismatch | Fix logic or update expectation |
| `X.testY(): threw error "E"` | Unexpected error thrown | Add error handling or fix the cause |
| `Test timed out after X seconds` | Deadlock or infinite loop | Check async code, add timeouts |

---

### clean

Cleans build artifacts.

**When to use:** When builds fail with stale cache issues, or after significant refactoring.

```
clean
  project: "MyApp.xcodeproj"
  scheme: "MyApp"
```

---

### list_simulators

Lists available simulators.

**When to use:** To find simulator names for build/test/boot commands.

```
list_simulators
```

**Typical output:**
```
Available simulators:
- iPhone 16 Pro (iOS 18.0) [Booted]
- iPhone 16 (iOS 18.0) [Shutdown]
- iPad Pro 13-inch (M4) (iPadOS 18.0) [Shutdown]
- Mac Catalyst [Available]
```

---

### boot_simulator

Boots a simulator by name.

**When to use:** Before installing or launching an app.

```
boot_simulator
  simulator: "iPhone 16 Pro"
```

---

### install_app

Installs a built app on a booted simulator.

**When to use:** After a successful build, to test the app visually.

```
install_app
  simulator: "iPhone 16 Pro"
  app_path: "/path/to/Build/Products/Debug-iphonesimulator/MyApp.app"
```

The app path is typically shown in the build output.

---

### launch_app

Launches an installed app on a booted simulator.

**When to use:** After installing, to start the app for testing or screenshots.

```
launch_app
  simulator: "iPhone 16 Pro"
  bundle_id: "com.example.MyApp"
```

---

### capture_logs

Captures console logs from a running app.

**When to use:** To debug runtime issues, crashes, or unexpected behavior.

```
capture_logs
  simulator: "iPhone 16 Pro"
  bundle_id: "com.example.MyApp"
  duration: 10  # seconds to capture
```

**Log analysis patterns:**

| Log Pattern | Meaning |
|------------|---------|
| `Fatal error: ...` | Runtime crash -- read the message |
| `Thread 1: signal SIGABRT` | Forced abort, often from `fatalError()` or force unwrap |
| `[SwiftData] error: ...` | Database operation failed |
| `nw_connection_...` | Network layer issue |
| `Unbalanced calls to begin/end` | UI update outside main thread |

---

### screenshot

Captures a screenshot of the current simulator state.

**When to use:** To verify visual appearance after UI changes.

```
screenshot
  simulator: "iPhone 16 Pro"
  output_path: "/tmp/screenshot.png"
```

---

### swift_package_test

Runs tests for a Swift Package (no Xcode project needed).

**When to use:** For Swift Package Manager projects without `.xcodeproj`.

```
swift_package_test
  package_path: "/path/to/Package"
  filter: "NetworkTests"  # optional: filter by test name
```

---

## Common Workflows

### Workflow 1: Build-Test Cycle (Most Common)

This is the standard loop during implementation:

```
1. discover_projects                    → Identify project
2. build_sim_name_proj                  → Build
   ├── Success → continue
   └── Failure → read errors, fix, rebuild
3. test_sim_name_proj                   → Run tests
   ├── All pass → task complete
   └── Failures → read output, fix, retest
```

### Workflow 2: Build-Run-Screenshot

For visual verification of UI work:

```
1. build_sim_name_proj                  → Build app
2. list_simulators                      → Find available simulator
3. boot_simulator                       → Start simulator
4. install_app                          → Install built app
5. launch_app                           → Open app
6. screenshot                           → Capture current state
```

### Workflow 3: Error Diagnosis Loop

When something is broken and you need to investigate:

```
1. build_sim_name_proj                  → Attempt build
   └── Read error messages carefully
2. Fix the identified issue
3. build_sim_name_proj                  → Rebuild
   ├── New error → back to step 2
   └── Success → continue
4. test_sim_name_proj                   → Run tests
5. If runtime issue:
   a. boot_simulator
   b. install_app + launch_app
   c. capture_logs                      → Read runtime output
   d. Fix issue, rebuild, retest
```

### Workflow 4: Swift Package Development

For library/framework work without an Xcode project:

```
1. discover_projects                    → Find Package.swift
2. swift_package_test                   → Run all tests
   ├── Success → continue
   └── Failure → fix, retest
3. swift_package_test filter:"specific" → Run targeted tests
```

### Workflow 5: Clean Build (Stale Cache)

When builds behave strangely after refactoring:

```
1. clean                                → Remove build artifacts
2. build_sim_name_proj                  → Fresh build
3. test_sim_name_proj                   → Verify tests still pass
```

---

## Tips

### Choosing a Simulator

- Use **iPhone 16 Pro** as the default (latest standard device)
- Use **iPad Pro** when testing iPad-specific layouts
- Use **iPhone SE** when testing compact size classes
- Prefer already-booted simulators (faster)

### Build Configuration

- Use **Debug** during development (faster compilation, better errors)
- Use **Release** only when testing performance or App Store builds

### Test Filtering

Run specific test suites to speed up the feedback loop:
```
test_sim_name_proj
  test_identifier: "UserServiceTests/testFetchProfile"
```

Pattern: `SuiteName/testMethodName` for XCTest, `SuiteName` for Swift Testing suites.

### Interpreting Build Times

| Duration | Assessment |
|----------|-----------|
| < 10s | Incremental build, normal |
| 10-30s | Moderate changes, normal |
| 30-60s | Many files changed or clean build |
| > 60s | Consider if a clean was needed or if there is a build config issue |

### Common Gotchas

1. **Simulator not found:** Run `list_simulators` to verify exact name spelling
2. **Build succeeds but tests fail to launch:** The test scheme may differ from the app scheme
3. **"No such module" after adding dependency:** Clean and rebuild; SPM may need to resolve
4. **Tests pass individually but fail together:** Shared mutable state between tests -- isolate properly
5. **Screenshot is blank:** Wait a moment after `launch_app` for the UI to render, then screenshot
