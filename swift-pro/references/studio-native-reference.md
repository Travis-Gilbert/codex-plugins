# Studio Native Reference Architecture

## Overview

Canonical reference for **CommonPlace Studio** — a cross-platform writing app
with a Tiptap rich-text editor inside a native SwiftUI shell. Demonstrates
every pattern the swift-pro plugin teaches in one coherent architecture.

**Stack:** SwiftUI shell, WKWebView (Tiptap, 17 extensions), SwiftData local
cache, Django REST API, actor-based APIClient, push-dirty-first SyncEngine,
StudioKit shared SPM package.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  CommonPlace Studio                      │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SwiftUI Shell (NavigationSplitView / TabView)   │   │
│  │  Toolbar, Menus, Settings, Navigation            │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │                                  │
│  ┌────────────────────▼─────────────────────────────┐   │
│  │  WKWebView (Tiptap Editor, 17 Extensions)        │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │ EditorBridge (JS <-> Swift)      │
│  ┌────────────────────▼─────────────────────────────┐   │
│  │  StudioKit (SPM)                                 │   │
│  │  @Model  |  SyncEngine (actor)  |  APIClient     │   │
│  │  isDirty |  pushDirty/pullAll   |  Bearer auth   │   │
│  └──────┬──────────────────────────────┬────────────┘   │
│    SwiftData                      URLSession             │
└─────────────────────────────────────────┬───────────────┘
                                          ▼
                                 Django REST API (DRF)
```

---

## SwiftData Models

```swift
@Model
public class ContentItem {
    public var title: String
    public var body: String          // Markdown from Tiptap
    public var excerpt: String       // First 200 chars plain text
    public var wordCount: Int
    public var createdAt: Date
    public var updatedAt: Date
    public var isPinned: Bool
    public var isArchived: Bool
    public var workspace: Workspace?
    @Relationship(inverse: \Tag.items) public var tags: [Tag]

    // Sync bookkeeping
    public var isDirty: Bool
    public var lastSyncedAt: Date?
    public var serverUpdatedAt: Date?
    public var serverID: String?
    public var isDeleted: Bool
    public var deletedAt: Date?

    #Unique<ContentItem>([\.serverID])
    #Index<ContentItem>([\.isDirty], [\.updatedAt], [\.isPinned])

    public init(title: String, body: String, workspace: Workspace? = nil) {
        self.title = title; self.body = body
        self.excerpt = String(body.prefix(200))
        self.wordCount = body.split(separator: " ").count
        self.createdAt = .now; self.updatedAt = .now
        self.isPinned = false; self.isArchived = false
        self.workspace = workspace; self.tags = []
        self.isDirty = true; self.isDeleted = false
    }

    public func markEdited(body: String, wordCount: Int) {
        self.body = body; self.excerpt = String(body.prefix(200))
        self.wordCount = wordCount; self.updatedAt = .now; self.isDirty = true
    }
}

@Model
public class Workspace {
    public var name: String
    public var icon: String               // SF Symbol
    public var sortOrder: Int
    public var serverID: String?
    public var isDirty: Bool
    @Relationship(deleteRule: .nullify) public var items: [ContentItem]

    public init(name: String, icon: String = "folder", sortOrder: Int = 0) {
        self.name = name; self.icon = icon; self.sortOrder = sortOrder
        self.items = []; self.isDirty = true
    }
}

@Model
public class Tag {
    public var name: String
    public var color: String              // Hex
    public var serverID: String?
    public var isDirty: Bool
    public var items: [ContentItem]

    public init(name: String, color: String = "#6B7280") {
        self.name = name; self.color = color; self.items = []; self.isDirty = true
    }
}
```

---

## APIClient Actor

```swift
public actor APIClient {
    private let baseURL: URL
    private let session: URLSession
    private var accessToken: String?
    private var refreshToken: String?
    private let tokenStore: TokenStore

    public init(baseURL: URL, tokenStore: TokenStore = .keychain) {
        self.baseURL = baseURL
        self.session = URLSession(configuration: .default)
        self.tokenStore = tokenStore
        self.accessToken = tokenStore.loadAccessToken()
        self.refreshToken = tokenStore.loadRefreshToken()
    }

    public func login(email: String, password: String) async throws {
        let response: TokenResponse = try await post("/auth/token/",
            body: LoginRequest(email: email, password: password), authenticated: false)
        self.accessToken = response.access
        self.refreshToken = response.refresh
        tokenStore.saveTokens(access: response.access, refresh: response.refresh)
    }

    // Auto-refresh on 401: perform() detects 401, refreshes token, retries once
    private func perform<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw APIError.requestFailed }
        if http.statusCode == 401 {
            try await refreshAccessToken()
            var retry = request
            retry.setValue("Bearer \(accessToken!)", forHTTPHeaderField: "Authorization")
            let (retryData, retryResp) = try await session.data(for: retry)
            guard let rh = retryResp as? HTTPURLResponse, (200..<300).contains(rh.statusCode) else {
                throw APIError.requestFailed
            }
            return try JSONDecoder.api.decode(T.self, from: retryData)
        }
        guard (200..<300).contains(http.statusCode) else {
            throw APIError.httpError(statusCode: http.statusCode, data: data)
        }
        return try JSONDecoder.api.decode(T.self, from: data)
    }
}
```

---

## EditorBridge: Two-Way JS Communication

The bridge handles all 17 Tiptap extension interactions:

| Extension Group | Bridge Messages |
|----------------|----------------|
| StarterKit, History | contentChanged, undoStateChanged |
| TaskList, Table | taskToggled, tableInserted |
| CodeBlock, Image | languageChanged, imageInsertRequested |
| SlashCommand, Link | slashCommand, linkTapped |
| FloatingMenu, BubbleMenu | menuShown, menuAction, bubbleAction |
| CharacterCount, Focus | countUpdated, focusChanged |

See `webview-bridge-patterns.md` for the full `EditorBridge` class,
`EditorCommand` enum, and `escapeForJS` implementation.

---

## Platform: macOS (NavigationSplitView)

```swift
struct MacContentView: View {
    @State private var selectedWorkspace: Workspace?
    @State private var selectedItem: ContentItem?

    var body: some View {
        NavigationSplitView {
            SidebarView(selection: $selectedWorkspace)
        } content: {
            if let workspace = selectedWorkspace {
                NoteListView(workspace: workspace, selection: $selectedItem)
            } else {
                AllNotesView(selection: $selectedItem)
            }
        } detail: {
            if let item = selectedItem {
                EditorContainerView(item: item)
            } else {
                ContentUnavailableView("Select a Note", systemImage: "doc.text")
            }
        }
    }
}
```

**macOS-specific features:**
- Global quick capture shortcut (Cmd+Shift+N via CGEvent tap)
- Native menu bar with Format commands (Bold, Italic, Heading via `CommandMenu`)
- Quick capture floating panel (`NSPanel` subclass)

## Platform: iOS (TabView)

```swift
struct iOSContentView: View {
    @State private var selectedTab: Tab = .notes
    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("Notes", systemImage: "doc.text", value: .notes) {
                NavigationStack { AllNotesView() }
            }
            Tab("Workspaces", systemImage: "folder", value: .workspaces) {
                NavigationStack { WorkspaceListView() }
            }
            Tab("Search", systemImage: "magnifyingglass", value: .search) {
                NavigationStack { SearchView() }
            }
            Tab("Settings", systemImage: "gear", value: .settings) {
                NavigationStack { SettingsView() }
            }
        }
    }
    enum Tab: Hashable { case notes, workspaces, search, settings }
}
```

**iOS-specific features:**
- Share Extension (receives text, creates ContentItem in shared App Group container)
- WidgetKit quick capture (deep link `commonplace://new-note`)
- System notifications for sync conflicts

---

## File Structure

```
CommonPlace/
├── StudioKit/                     # Shared SPM Package
│   ├── Package.swift
│   ├── Sources/StudioKit/
│   │   ├── Models/                # ContentItem, Workspace, Tag, ContainerSetup
│   │   ├── Sync/                  # SyncEngine, SyncState, ConflictResolver
│   │   ├── API/                   # APIClient, ServerModels, TokenStore
│   │   ├── Bridge/                # EditorBridge, EditorCommand, MessageTypes
│   │   └── Utilities/             # KeychainHelper, DateFormatting
│   └── Tests/StudioKitTests/
├── EditorBundle/                  # Bundled Tiptap (esbuild output)
│   ├── index.html, editor.js, editor.css
│   └── build/                     # Source TS, build config
├── CommonPlaceMac/                # macOS Target
│   ├── App/, Views/, Platform/    # NSViewRepresentable, GlobalShortcuts, MenuBar
├── CommonPlaceiOS/                # iOS Target
│   ├── App/, Views/, Platform/    # UIViewRepresentable, ShareExtension
├── CommonPlaceShareExtension/     # iOS Share Extension
└── CommonPlaceWidgets/            # WidgetKit
```

---

## Layer Responsibilities

| Layer | Owns | Does Not Own |
|-------|------|-------------|
| SwiftUI Shell | Navigation, toolbar, settings | Content editing, API calls |
| WKWebView (Tiptap) | Rich text editing, undo/redo | Persistence, network |
| EditorBridge | Message routing, escaping | Business logic, storage |
| StudioKit Models | Schema, validation, sync fields | UI presentation |
| SyncEngine | Push/pull, conflicts, scheduling | Authentication, UI state |
| APIClient | HTTP, auth tokens, JSON | Business rules |
| Platform Targets | OS-specific views, extensions | Shared logic |

---

## Data Flow: User Edits a Note

1. User types in Tiptap (WKWebView)
2. Tiptap `onUpdate` fires -> JS calls `sendToSwift("contentChanged", { markdown, wordCount })`
3. `EditorBridge` routes to `delegate.editorContentDidChange(markdown:wordCount:)`
4. `EditorContainerView` calls `item.markEdited(body:wordCount:)`
5. SwiftData auto-saves (`isDirty = true`)
6. Next `SyncEngine.sync()`: `pushDirty()` sends PUT -> server responds -> `markSynced()`

## Data Flow: App Launches

1. `App.init()` creates `ModelContainer` via `StudioContainer.create()`
2. `.task {}` fires -> `syncEngine.sync()` (push offline edits, then pull)
3. SwiftData updates trigger SwiftUI view refreshes
4. `startPeriodicSync(interval: 30)` begins timer

---

## What This Architecture Enables

- **Offline-first** — full editing without network; sync catches up when online
- **Cross-platform** — one codebase for models, sync, API; platform targets only contain views
- **Rich editing** — Tiptap provides world-class editor without building natively
- **Testable** — `swift test` on StudioKit, no simulator needed
- **Extensible** — new Tiptap extensions add editor features without touching Swift
- **Secure** — tokens in Keychain, no credentials in WebView, actor-isolated API
