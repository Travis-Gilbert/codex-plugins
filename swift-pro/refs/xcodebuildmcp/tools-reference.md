# XcodeBuildMCP Tools Reference

> Complete inventory of XcodeBuildMCP MCP tools with parameters and usage patterns.

## Installation

```bash
claude mcp add --transport stdio XcodeBuildMCP -- npx -y xcodebuildmcp@latest
```

## Tool Inventory

### Project Discovery

#### `mcp__xcodebuildmcp__discover_projects`
Discovers Xcode projects and workspaces in the current directory.

**Parameters**: None (scans current working directory)
**Returns**: List of .xcodeproj and .xcworkspace files with schemes and targets.
**Use first**: Always call this before any build/test operation to get the correct scheme name.

### Build Operations

#### `mcp__xcodebuildmcp__build_sim_name_proj`
Builds the project for a simulator destination.

**Parameters**:
- `scheme` (string): The scheme to build
- `simulator` (string): Simulator name (e.g., "iPhone 16 Pro")
- `project` or `workspace` (string): Path to .xcodeproj or .xcworkspace
- `configuration` (string, optional): Build configuration (default: "Debug")
- `derivedDataPath` (string, optional): Custom DerivedData path
- `extraArgs` (string[], optional): Additional xcodebuild arguments

**Returns**: Build result with errors, warnings, and build log path.

**Example workflow**:
```
1. discover_projects -> get scheme name
2. build_sim_name_proj(scheme: "MyApp", simulator: "iPhone 16 Pro")
3. Parse build output for errors/warnings
```

#### `mcp__xcodebuildmcp__clean`
Cleans build artifacts.

**Parameters**:
- `scheme` (string): The scheme to clean
- `project` or `workspace` (string): Path
- `derivedDataPath` (string, optional): Custom DerivedData path

**Use when**: Build cache issues, switching configurations, or starting fresh.

### Test Operations

#### `mcp__xcodebuildmcp__test_sim_name_proj`
Runs tests for a scheme on a simulator.

**Parameters**:
- `scheme` (string): The scheme containing tests
- `simulator` (string): Simulator name
- `project` or `workspace` (string): Path
- `testIdentifier` (string, optional): Run specific test (e.g., "MyAppTests/ContentObjectTests/testCreate")
- `testPlan` (string, optional): Specific test plan to run
- `configuration` (string, optional): Build configuration
- `extraArgs` (string[], optional): Additional xcodebuild arguments

**Returns**: Test results with pass/fail/skip counts, individual test outcomes, and failure details.

#### `mcp__xcodebuildmcp__swift_package_test`
Runs tests for a Swift package (no Xcode project needed).

**Parameters**:
- `path` (string): Path to Swift package directory
- `filter` (string, optional): Test name filter regex
- `parallel` (boolean, optional): Run tests in parallel (default: true)

**Use when**: Testing Swift packages independently of the main app.

### Simulator Management

#### `mcp__xcodebuildmcp__list_simulators`
Lists available simulators.

**Parameters**:
- `filter` (string, optional): Filter by name, OS, or device type

**Returns**: List of simulators with name, UDID, state (booted/shutdown), runtime.

#### `mcp__xcodebuildmcp__boot_simulator`
Boots a simulator.

**Parameters**:
- `simulator` (string): Simulator name or UDID

**Note**: Build/test operations auto-boot if needed, but explicit boot is faster for repeated operations.

### App Operations

#### `mcp__xcodebuildmcp__install_app`
Installs a built app on a simulator.

**Parameters**:
- `appPath` (string): Path to .app bundle (from build output)
- `simulator` (string): Simulator name or UDID

#### `mcp__xcodebuildmcp__launch_app`
Launches an installed app on a simulator.

**Parameters**:
- `bundleId` (string): App bundle identifier
- `simulator` (string): Simulator name or UDID
- `args` (string[], optional): Launch arguments
- `env` (object, optional): Environment variables

### Diagnostics

#### `mcp__xcodebuildmcp__capture_logs`
Captures device/simulator logs.

**Parameters**:
- `simulator` (string): Simulator name or UDID
- `duration` (number, optional): Seconds to capture (default: 10)
- `filter` (string, optional): Log filter predicate
- `bundleId` (string, optional): Filter by app bundle ID
- `level` (string, optional): Minimum log level: "debug", "info", "error", "fault"

**Use when**: Debugging runtime issues, crash investigation.

#### `mcp__xcodebuildmcp__screenshot`
Takes a screenshot of the simulator screen.

**Parameters**:
- `simulator` (string): Simulator name or UDID
- `outputPath` (string): Where to save the screenshot
- `format` (string, optional): Image format: "png" (default), "jpeg", "tiff"

**Use when**: Verifying UI appearance, documenting features, debugging layout.

## Common Workflows

### Build-Test Cycle
```
1. discover_projects
2. build_sim_name_proj (verify compilation)
3. test_sim_name_proj (run tests)
4. If failures: read error, fix, repeat from 2
```

### Build-Run-Screenshot
```
1. discover_projects
2. build_sim_name_proj
3. boot_simulator (if not already booted)
4. install_app
5. launch_app
6. Wait briefly, then screenshot
```

### Debug with Logs
```
1. launch_app(simulator: "iPhone 16 Pro", bundleId: "com.example.App")
2. capture_logs(simulator: "iPhone 16 Pro", bundleId: "com.example.App", level: "error")
3. screenshot(simulator: "iPhone 16 Pro", outputPath: "/tmp/debug.png")
```

### Error Diagnosis Loop
```
1. build_sim_name_proj
2. Parse errors from output
3. For each error:
   a. Classify (concurrency, type, import, syntax)
   b. Read relevant source file
   c. Fix the error
   d. Rebuild to verify
4. When clean: run tests
```

## Build Error Classification

| Error Pattern | Category | Agent to Load |
|---------------|----------|---------------|
| "Capture of non-Sendable" | Concurrency | concurrency-specialist |
| "actor-isolated" | Concurrency | concurrency-specialist |
| "Cannot convert value of type" | Type mismatch | (context-dependent) |
| "No such module" | Missing import | (check dependencies) |
| "Cannot find type/value" | Missing declaration | (check spelling/imports) |
| "Ambiguous use of" | Overload resolution | (add type annotation) |
| "@Observable" errors | Observation | swiftui-builder |
| "@Query" / "@Model" errors | SwiftData | swiftdata-engineer |
| Layout constraint warnings | SwiftUI | swiftui-builder |
