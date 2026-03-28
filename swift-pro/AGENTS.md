# Swift-Pro Agent Registry

> Agent routing rules for the Swift-Pro plugin. Claude Code reads this
> to determine which specialist to load for a given task.

## Agent Selection

Agents are composable context, not exclusive. A single task may load
multiple agents. Read the relevant agent .md file(s) before starting work.

### By Task Type

| Task | Primary Agent | Also Load | Key Refs |
|------|--------------|-----------|----------|
| New app scaffold | `swift-architect` | `swiftui-builder` | `references/mvvm-observable.md` |
| Feature module structure | `swift-architect` | -- | `references/mvvm-observable.md` |
| Navigation architecture | `swift-architect` | `swiftui-builder` | `references/navigation-patterns.md` |
| MVVM setup | `swift-architect` | -- | `references/mvvm-observable.md`, `refs/observation/` |
| SwiftUI view creation | `swiftui-builder` | -- | `refs/observation/`, `references/swiftui-modern-patterns.md` |
| View extraction/refactor | `swiftui-builder` | -- | `references/swiftui-modern-patterns.md` |
| Custom layout/animation | `swiftui-builder` | -- | -- |
| Accessibility | `swiftui-builder` | -- | -- |
| SwiftData models | `swiftdata-engineer` | -- | `refs/swiftdata/`, `references/swiftdata-patterns.md` |
| Data migration | `swiftdata-engineer` | -- | `refs/swiftdata/Schema.swift` |
| @Query optimization | `swiftdata-engineer` | -- | `refs/swiftdata/Query.swift` |
| CloudKit + SwiftData | `swiftdata-engineer` | `platform-integrator` | `references/swiftdata-patterns.md` |
| Async/await patterns | `concurrency-specialist` | -- | `refs/swift-concurrency/`, `references/swift6-concurrency.md` |
| Actor isolation | `concurrency-specialist` | -- | `refs/swift-concurrency/Actor.swift` |
| Sendable conformance | `concurrency-specialist` | -- | `references/swift6-concurrency.md` |
| Task groups / async sequences | `concurrency-specialist` | -- | `refs/swift-concurrency/` |
| Fixing concurrency warnings | `concurrency-specialist` | -- | `references/swift6-concurrency.md` |
| Spotlight integration | `platform-integrator` | -- | `references/platform-integration-catalog.md` |
| WidgetKit extension | `platform-integrator` | `swiftui-builder` | `references/platform-integration-catalog.md` |
| Share Extension | `platform-integrator` | -- | `references/platform-integration-catalog.md` |
| Shortcuts / Intents | `platform-integrator` | -- | `references/platform-integration-catalog.md` |
| Push notifications (APNs) | `platform-integrator` | `networking-engineer` | `references/platform-integration-catalog.md` |
| URLSession networking | `networking-engineer` | `concurrency-specialist` | `references/networking-patterns.md` |
| Token auth (JWT) | `networking-engineer` | -- | `references/networking-patterns.md` |
| API client design | `networking-engineer` | -- | `references/networking-patterns.md` |
| Codable models | `networking-engineer` | -- | -- |
| macOS window architecture | `appkit-specialist` | -- | `refs/appkit-patterns/`, `references/appkit-macos-patterns.md` |
| NSToolbar | `appkit-specialist` | -- | `refs/appkit-patterns/NSToolbar.md` |
| NSSplitViewController | `appkit-specialist` | -- | `refs/appkit-patterns/NSSplitViewController.md` |
| NSOutlineView (sidebar) | `appkit-specialist` | -- | `refs/appkit-patterns/NSOutlineView.md` |
| macOS menus | `appkit-specialist` | -- | `references/appkit-macos-patterns.md` |
| SwiftUI in AppKit host | `appkit-specialist` | `swiftui-builder` | `references/appkit-macos-patterns.md` |
| WKWebView editor setup | `webview-bridge` | `appkit-specialist` | `refs/wkwebview/`, `references/webview-bridge-patterns.md` |
| JS-to-Swift bridge | `webview-bridge` | -- | `refs/wkwebview/WKScriptMessageHandler.md` |
| Bundled editor extraction | `webview-bridge` | -- | `references/webview-bridge-patterns.md` |
| Editor command dispatch | `webview-bridge` | -- | `references/webview-bridge-patterns.md` |
| Background sync engine | `swiftdata-engineer` | `networking-engineer` | `references/sync-engine-patterns.md` |
| isDirty tracking | `swiftdata-engineer` | -- | `references/sync-engine-patterns.md` |
| Conflict resolution | `swiftdata-engineer` | -- | `references/sync-engine-patterns.md` |
| Shared Swift package | `swift-architect` | -- | `references/shared-package-architecture.md` |
| macOS + iOS dual target | `swift-architect` | -- | `references/shared-package-architecture.md` |
| Unit tests | `test-engineer` | -- | `refs/swift-testing/`, `references/testing-strategy.md` |
| UI tests | `test-engineer` | -- | `references/testing-strategy.md` |
| Build errors | `test-engineer` | (domain agent) | `references/xcodebuildmcp-usage.md` |
| Test coverage | `test-engineer` | -- | `references/testing-strategy.md` |

### Slash Commands

| Command | Agent/File | Description |
|---------|-----------|-------------|
| `/swift` | `agents/swift-architect.md` | Plugin hub: routes to the right specialist |
| `/view` | `agents/swiftui-builder.md` | Create or refactor SwiftUI views |
| `/model` | `agents/swiftdata-engineer.md` | SwiftData models and queries |
| `/async` | `agents/concurrency-specialist.md` | Concurrency patterns and fixes |
| `/integrate` | `agents/platform-integrator.md` | Platform features (Spotlight, Widgets, etc.) |
| `/network` | `agents/networking-engineer.md` | URLSession, API client, auth |
| `/appkit` | `agents/appkit-specialist.md` | macOS AppKit patterns |
| `/bridge` | `agents/webview-bridge.md` | WKWebView editor + JS bridge |
| `/test` | `agents/test-engineer.md` | Testing and build operations |
| `/build` | `commands/build.md` | Build via XcodeBuildMCP |
| `/run` | `commands/run-app.md` | Build + launch on simulator |
| `/fix` | `commands/fix-build.md` | Diagnose and fix build errors |
| `/feature` | `commands/create-feature.md` | Scaffold a feature module |
| `/prd` | `commands/create-prd.md` | Create PRD from discussion |
| `/spec` | `commands/generate-spec.md` | Generate feature spec from PRD |
| `/tasks` | `commands/generate-tasks.md` | Break spec into tasks |
| `/plan` | `commands/plan-feature.md` | Plan-mode analysis (Opus) |

### Composition Rules

- When building a feature with SwiftData persistence, load BOTH
  swiftui-builder AND swiftdata-engineer. The view needs @Query
  and the model needs @Model; they must agree on the schema.
- When networking touches concurrency (async sequences, actor-isolated
  API clients), load BOTH networking-engineer AND concurrency-specialist.
- When building a macOS app with SwiftUI views hosted in AppKit
  containers, load BOTH appkit-specialist AND swiftui-builder.
- When implementing a Widget extension, load BOTH platform-integrator
  AND swiftui-builder (Widgets are SwiftUI views with a timeline provider).
- When fixing build errors, the test-engineer loads the relevant domain
  agent based on the error type (concurrency warning loads concurrency-
  specialist, SwiftUI layout error loads swiftui-builder, etc.).
- When building a hybrid native/web app with a WKWebView editor, load
  BOTH webview-bridge AND the platform agent (appkit-specialist for macOS,
  swiftui-builder for iOS). The bridge owns JS communication; the platform
  agent owns the native container.
- When implementing background sync with SwiftData, load BOTH
  swiftdata-engineer AND networking-engineer. The sync engine sits at the
  intersection of local persistence and network requests.
- When scaffolding a macOS + iOS app with a shared package, load
  swift-architect first for the workspace structure, then the relevant
  platform agent for each target's views.
