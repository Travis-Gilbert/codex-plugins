# Swift-Pro Plugin

You have access to Swift concurrency module source, Observation framework
internals (@Observable), SwiftData framework patterns, Swift Testing
framework source, AppKit reference patterns, WKWebView bridge patterns,
and XcodeBuildMCP tool documentation. Use them.

## Critical: XcodeBuildMCP

This plugin assumes XcodeBuildMCP is installed and available. All build,
test, run, and debug operations go through XcodeBuildMCP tools. Do NOT
suggest manual xcodebuild commands or ask the user to open Xcode.

Verify XcodeBuildMCP is available at the start of every session:
- Run `mcp__xcodebuildmcp__discover_projects` to confirm connectivity
- If it fails, instruct the user to install XcodeBuildMCP:
  `claude mcp add --transport stdio XcodeBuildMCP -- npx -y xcodebuildmcp@latest`

## When You Start a Swift Task

1. Determine the task category. Read the relevant agent in agents/.
2. Check refs/ for the frameworks you will use. Grep the source to
   verify API signatures rather than relying on memory.
3. If the task involves architecture, read references/mvvm-observable.md
   to confirm you are using @Observable, NOT ObservableObject.
4. If the task involves persistence, read references/swiftdata-patterns.md
   to confirm you are using SwiftData, NOT Core Data (unless the project
   explicitly uses Core Data).
5. If the task involves concurrency, read references/swift6-concurrency.md
   to confirm your code passes Swift 6 strict concurrency checking.
6. If the task involves macOS, read references/appkit-macos-patterns.md
   to understand the window/toolbar/sidebar conventions.
7. If the task involves a WKWebView editor or JS bridge, read
   references/webview-bridge-patterns.md to understand the message
   passing architecture before writing any bridge code.
8. If the task involves background sync with a server API, read
   references/sync-engine-patterns.md to understand the push-dirty-first
   protocol and isDirty tracking before implementing sync logic.
9. If the task involves a macOS + iOS shared codebase, read
   references/shared-package-architecture.md for the SPM workspace
   pattern before creating project structure.
10. After writing code, ALWAYS build via XcodeBuildMCP to verify it compiles.

## Source References

Framework source and patterns are in refs/. Use them to verify API details:
- Swift concurrency (actors, tasks, async sequences): refs/swift-concurrency/
- Observation framework (@Observable, @Bindable): refs/observation/
- SwiftData (@Model, @Query, ModelContainer): refs/swiftdata/
- Swift Testing (@Test, #expect): refs/swift-testing/
- macOS AppKit patterns: refs/appkit-patterns/
- WKWebView bridge patterns: refs/wkwebview/
- XcodeBuildMCP tools: refs/xcodebuildmcp/tools-reference.md

## Reference Library

Curated knowledge docs in references/. Read before starting:
- swift6-concurrency.md: Strict concurrency, Sendable, actor isolation
- swiftui-modern-patterns.md: @Observable, NavigationStack, @Bindable
- swiftdata-patterns.md: @Model, @Query, ModelContainer, migration
- mvvm-observable.md: MVVM with @Observable (not ObservableObject)
- navigation-patterns.md: NavigationStack, type-safe routing, deep links
- networking-patterns.md: URLSession async, Codable, token auth
- appkit-macos-patterns.md: Window, toolbar, sidebar, menus
- platform-integration-catalog.md: Spotlight, Widgets, Extensions, etc.
- testing-strategy.md: Swift Testing vs XCTest, coverage
- prd-workflow.md: PRD-driven development process
- xcodebuildmcp-usage.md: Build, test, run, debug via MCP
- api-design-guidelines.md: Apple's naming conventions
- webview-bridge-patterns.md: WKWebView + JS bridge, bundled editors
- sync-engine-patterns.md: Push-dirty-first, pull-all, conflict resolution
- shared-package-architecture.md: SPM shared package for macOS + iOS
- studio-native-reference.md: Real-world hybrid native/web app architecture

## Rules

1. NEVER use ObservableObject or @Published. Use @Observable and @Bindable.
   ObservableObject is the iOS 13-16 pattern. @Observable (Observation
   framework, iOS 17+) is the current standard. It provides more granular
   view updates, less boilerplate, and works with @Bindable for bindings.
   The ONLY exception is when the project explicitly targets iOS 16 or
   earlier.

2. NEVER use NavigationView. Use NavigationStack with type-safe routing.
   NavigationView is deprecated. NavigationStack with a `path` binding
   and `.navigationDestination(for:)` is the current pattern.

3. NEVER use Core Data when SwiftData is available. SwiftData is the
   modern persistence framework for iOS 17+. Use @Model, @Query,
   ModelContainer, ModelContext. The ONLY exception is when the project
   explicitly uses Core Data or needs features SwiftData does not yet
   support.

4. NEVER ignore Swift 6 strict concurrency warnings. Every warning is a
   potential data race. Use @Sendable, @MainActor, actor isolation, and
   structured concurrency to resolve warnings. Do not suppress them.

5. NEVER write SwiftUI views longer than 100 lines. Extract subviews.
   A view file should contain the view struct, its preview, and nothing
   else. ViewModel logic belongs in a separate @Observable class.

6. NEVER write code without building it via XcodeBuildMCP afterward.
   Swift is a compiled language. Code that Claude Code writes but does
   not compile is worse than no code at all. Build after every
   significant change.

7. NEVER use force unwrapping (`!`) without documenting why it is safe.
   If you cannot explain why the optional will never be nil at that point,
   use `guard let` or `if let` instead.

8. NEVER write networking code with URLSession without handling errors
   and status codes. Every network call needs: error handling, HTTP
   status code checking, response decoding with typed errors, and
   cancellation support via Task.

9. For macOS apps, NEVER build a SwiftUI-only app when the design calls
   for AppKit patterns (NSOutlineView for source lists, NSToolbar for
   toolbars, NSSplitViewController for split views). SwiftUI hosting
   inside AppKit containers is the correct hybrid pattern for production
   macOS apps that need full native integration.

10. When embedding a web editor (Tiptap, ProseMirror, CodeMirror, Monaco)
    in a native app via WKWebView, NEVER have the editor call the backend
    API directly. All API calls go through the native bridge: the JS editor
    sends a message to Swift via WKScriptMessageHandler, Swift makes the
    API call, Swift pushes the result back via evaluateJavaScript. This
    keeps auth tokens out of the WebView, enables offline queueing in
    SwiftData, and maintains the native app as the single source of truth
    for network state.

11. NEVER implement sync without pushing dirty records first. The correct
    sync cycle order is: (1) push local dirty items to server, (2) pull
    server state to local cache. If you pull first, you may overwrite
    local changes that have not been synced yet. Use isDirty flags on
    every @Model that can be edited locally, and clear the flag only
    after the server confirms the write.

12. When building a macOS + iOS app from a shared codebase, NEVER put
    shared logic in either app target. Create a Swift package (e.g.,
    StudioKit) that both targets import. The package contains: API
    clients, SwiftData models, sync engine, type definitions, and bridge
    protocols. App targets contain only platform-specific views, navigation,
    and system integration (menus, widgets, extensions).

13. ALWAYS follow Apple's Swift API Design Guidelines for naming. Methods
    read as English phrases. Boolean properties read as assertions.
    Protocols that describe capability use "-able" or "-ible" suffixes.
    Factory methods use "make" prefix. Read references/api-design-guidelines.md.

## A Note on Examples

Examples throughout this plugin use CommonPlace (an epistemic knowledge
graph tool) as the reference project. The domain language is CommonPlace-
specific, but every pattern is general. @Observable ViewModels work for
any app. NavigationStack routing works for any navigation hierarchy.
SwiftData models work for any persistence need. When applying these
patterns to a different project, substitute the domain objects but keep
the architectural structure intact.

## Cross-Reference with Other Plugins

- For web app transformation and Tauri desktop: defer to app-forge.
  Swift-Pro receives handoff documents from app-forge's swift-planner
  and implements them.
- For React Native mobile: defer to app-pro. Swift-Pro handles native
  iOS; app-pro handles cross-platform mobile.
- For Django backend API design: defer to Django-Engine-Pro. Swift-Pro
  specifies which endpoints the native app consumes; Django-Engine-Pro
  implements them.
- For D3 visualizations that will render in a WKWebView inside the
  native app: defer to D3-Pro.
- This plugin owns: Swift architecture, SwiftUI views, SwiftData
  persistence, Swift 6 concurrency, AppKit macOS patterns, platform
  integration (Spotlight, Widgets, Extensions), networking, testing,
  XcodeBuildMCP operations, and PRD-driven development workflow.
