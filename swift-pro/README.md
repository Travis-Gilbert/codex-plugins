# Swift-Pro: Claude Code Native iOS and macOS Development Plugin

A standalone Claude Code plugin that makes Claude Code extraordinarily good at building native iOS and macOS applications in Swift, with deep expertise in SwiftUI, Swift 6 concurrency, SwiftData, XcodeBuildMCP integration, PRD-driven workflows, and Apple platform conventions.

## What This Is

A skill directory for Claude Code containing agent definitions, Swift framework references, curated knowledge documents, and starter templates. When Claude Code works inside this directory (or a project that references it), it produces Swift code that follows Apple's API Design Guidelines, uses modern concurrency, leverages SwiftUI and SwiftData correctly, and builds/tests via XcodeBuildMCP without ever opening Xcode manually.

## What This Is NOT

A library, a Swift package, or anything that runs in production. Nothing here executes. It is all context and guidance for Claude Code.

## Prerequisites

- **Claude Code** installed and running
- **XcodeBuildMCP** for build/test/run operations:
  ```bash
  claude mcp add --transport stdio XcodeBuildMCP -- npx -y xcodebuildmcp@latest
  ```
- **Xcode** installed (XcodeBuildMCP uses it under the hood)
- **Node.js** (for npx/XcodeBuildMCP)

## Installation

### As a Claude Code Plugin (recommended)

The plugin is part of the codex-plugins repository. Run the sync script from the repo root:

```bash
./sync-plugins.sh
```

Then enable in `~/.claude/settings.json`:
```json
{
  "enabledPlugins": {
    "swift-pro@local-desktop-app-uploads": true
  }
}
```

### Global Install (standalone)

```bash
bash install.sh --global
```

This symlinks agents and commands into `~/.claude/` for use in any project.

### Local Install

```bash
bash install.sh
```

Run Claude Code from the swift-pro directory or a project that references it.

## Agents

| Agent | Command | Expertise |
|-------|---------|-----------|
| swift-architect | `/swift` | App architecture, MVVM, navigation, module structure |
| swiftui-builder | `/view` | SwiftUI views, @Observable, layout, animations |
| swiftdata-engineer | `/model` | SwiftData models, queries, migration, sync |
| concurrency-specialist | `/async` | Swift 6 async/await, actors, Sendable, isolation |
| platform-integrator | `/integrate` | Spotlight, Widgets, Extensions, Shortcuts, CloudKit |
| networking-engineer | `/network` | URLSession, API client, token auth, Codable |
| appkit-specialist | `/appkit` | macOS AppKit: windows, toolbar, sidebar, menus |
| test-engineer | `/test` | Swift Testing, XCTest, XcodeBuildMCP operations |

## Workflow Commands

| Command | Purpose |
|---------|---------|
| `/build` | Build via XcodeBuildMCP |
| `/run` | Build + launch on simulator |
| `/fix` | Diagnose and fix build errors |
| `/feature` | Scaffold a feature module |
| `/prd` | Create PRD from discussion |
| `/spec` | Generate feature spec from PRD |
| `/tasks` | Break spec into tasks |
| `/plan` | Plan-mode feature analysis |

## Key Rules

1. **@Observable**, not ObservableObject. @State, not @StateObject.
2. **NavigationStack**, not NavigationView.
3. **SwiftData**, not Core Data (for iOS 17+).
4. **Swift 6 strict concurrency** — zero warnings tolerated.
5. **Views under 100 lines** — extract subviews aggressively.
6. **Always build** via XcodeBuildMCP after writing code.
7. **No force unwrapping** without documented justification.
8. **Typed error handling** for all networking.
9. **AppKit containers** for production macOS (SwiftUI hosted inside).
10. **Apple API Design Guidelines** for all naming.

## Relationship to Other Plugins

- **app-forge**: Plans native app architecture. Swift-Pro receives handoffs and implements.
- **app-pro**: Owns React Native mobile. Swift-Pro owns native iOS/macOS.
- **django-engine-pro**: Implements the Django API that Swift-Pro's networking layer consumes.
- **d3-pro**: Handles D3 visualizations rendered in WKWebView inside native apps.

## Directory Structure

```
swift-pro/
├── CLAUDE.md              # Plugin root config
├── AGENTS.md              # Agent registry and routing
├── agents/                # 8 specialist agent definitions
├── refs/                  # Framework source references
├── references/            # 12 curated knowledge documents
├── templates/             # 7 starter scaffolds
├── commands/              # 12 slash commands
├── hooks/                 # SwiftLint + concurrency warning hooks
├── data/                  # Test fixtures
├── install.sh             # Install script
└── README.md              # This file
```

## Credit

The XcodeBuildMCP integration patterns and PRD-driven workflow in this plugin are adapted from [keskinonur/claude-code-ios-dev-guide](https://github.com/keskinonur/claude-code-ios-dev-guide).
