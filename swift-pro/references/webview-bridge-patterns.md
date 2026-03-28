# WKWebView + JavaScript Bridge Patterns

## Why WKWebView for Rich Text Editing

Native `TextEditor` provides basic plaintext. Building a full rich-text editor natively
would take months. Industry leaders use WKWebView to host a web-based editor:

| App | Editor Engine | Shell |
|-----|---------------|-------|
| Bear | Custom Markdown (WebView) | Native SwiftUI |
| Obsidian | CodeMirror (WebView) | Electron / native |
| Notion | ProseMirror (WebView) | Electron / native |
| Craft | Custom (WebView + native) | Native SwiftUI |

**Native shell owns navigation, persistence, sync, and platform features;
WebView owns the editing surface.**

---

## WKWebViewConfiguration Setup

```swift
import WebKit

final class EditorWebViewFactory {
    static func makeConfiguration(bridge: EditorBridge) -> WKWebViewConfiguration {
        let config = WKWebViewConfiguration()
        let contentController = WKUserContentController()

        // JS calls window.webkit.messageHandlers.editorBridge.postMessage()
        contentController.add(bridge, name: "editorBridge")

        let themeScript = WKUserScript(
            source: "document.documentElement.dataset.theme = 'dark';",
            injectionTime: .atDocumentStart, forMainFrameOnly: true
        )
        contentController.addUserScript(themeScript)
        config.userContentController = contentController
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        return config
    }

    static func loadBundledEditor(into webView: WKWebView) {
        guard let url = Bundle.main.url(forResource: "index", withExtension: "html",
                                        subdirectory: "EditorBundle") else {
            fatalError("EditorBundle/index.html not found")
        }
        webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
    }
}
```

---

## JS-to-Swift: WKScriptMessageHandler

```javascript
// In the editor JS
function sendToSwift(type, payload) {
    window.webkit?.messageHandlers?.editorBridge?.postMessage({ type, payload });
}
sendToSwift("contentChanged", { markdown: editor.getMarkdown(), wordCount: 342 });
sendToSwift("linkTapped", { url: "https://example.com" });
sendToSwift("slashCommand", { command: "insertImage" });
```

### Typed Message Parsing in Swift

```swift
enum EditorMessageType: String, Codable {
    case contentChanged, linkTapped, slashCommand, selectionChanged, editorReady, editorError
}

final class EditorBridge: NSObject, WKScriptMessageHandler {
    weak var delegate: EditorBridgeDelegate?

    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard let body = message.body as? [String: Any],
              let typeString = body["type"] as? String,
              let type = EditorMessageType(rawValue: typeString) else { return }

        let payload = body["payload"] as? [String: Any] ?? [:]

        switch type {
        case .contentChanged:
            guard let markdown = payload["markdown"] as? String else { return }
            delegate?.editorContentDidChange(markdown: markdown,
                                             wordCount: payload["wordCount"] as? Int ?? 0)
        case .linkTapped:
            guard let urlString = payload["url"] as? String,
                  let url = URL(string: urlString) else { return }
            delegate?.editorDidTapLink(url)
        case .slashCommand:
            guard let command = payload["command"] as? String else { return }
            delegate?.editorDidInvokeSlashCommand(command)
        case .selectionChanged:
            delegate?.editorSelectionDidChange(
                from: payload["from"] as? Int ?? 0,
                to: payload["to"] as? Int ?? 0,
                selectedText: payload["text"] as? String ?? "")
        case .editorReady:  delegate?.editorDidBecomeReady()
        case .editorError:  delegate?.editorDidEncounterError(payload["message"] as? String ?? "")
        }
    }
}

protocol EditorBridgeDelegate: AnyObject {
    func editorContentDidChange(markdown: String, wordCount: Int)
    func editorDidTapLink(_ url: URL)
    func editorDidInvokeSlashCommand(_ command: String)
    func editorSelectionDidChange(from: Int, to: Int, selectedText: String)
    func editorDidBecomeReady()
    func editorDidEncounterError(_ message: String)
}
```

---

## Swift-to-JS: EditorCommand with Content Escaping

```swift
enum EditorCommand {
    case setContent(markdown: String)
    case insertText(text: String)
    case toggleBold, toggleItalic
    case toggleHeading(level: Int)
    case insertLink(url: String, text: String)
    case setTheme(name: String)
    case focus, blur, undo, redo

    var javaScript: String {
        switch self {
        case .setContent(let md):  "window.editorAPI.setContent(\"\(Self.escapeForJS(md))\");"
        case .insertText(let t):   "window.editorAPI.insertText(\"\(Self.escapeForJS(t))\");"
        case .toggleBold:          "window.editorAPI.toggleBold();"
        case .toggleItalic:        "window.editorAPI.toggleItalic();"
        case .toggleHeading(let l): "window.editorAPI.toggleHeading(\(l));"
        case .insertLink(let u, let t):
            "window.editorAPI.insertLink(\"\(Self.escapeForJS(u))\", \"\(Self.escapeForJS(t))\");"
        case .setTheme(let n):     "window.editorAPI.setTheme(\"\(n)\");"
        case .focus: "window.editorAPI.focus();"
        case .blur:  "window.editorAPI.blur();"
        case .undo:  "window.editorAPI.undo();"
        case .redo:  "window.editorAPI.redo();"
        }
    }

    /// Escape for safe embedding in a JS string literal.
    /// Handles backslashes, quotes, newlines, backticks, dollar signs.
    static func escapeForJS(_ string: String) -> String {
        string
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
            .replacingOccurrences(of: "'", with: "\\'")
            .replacingOccurrences(of: "\n", with: "\\n")
            .replacingOccurrences(of: "\r", with: "\\r")
            .replacingOccurrences(of: "`", with: "\\`")      // template literals
            .replacingOccurrences(of: "$", with: "\\$")      // template interpolation
    }
}

extension WKWebView {
    func execute(_ command: EditorCommand) async throws {
        _ = try await evaluateJavaScript(command.javaScript)
    }
}
```

---

## Bundled Editor Extraction with esbuild

Extract a Tiptap editor from a Next.js project into standalone HTML/JS/CSS:

```typescript
// editor-standalone.ts — entry point for native bundle
import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";

const editor = new Editor({
    element: document.getElementById("editor")!,
    extensions: [StarterKit /* + your custom extensions */],
    onUpdate: ({ editor }) => {
        window.webkit?.messageHandlers?.editorBridge?.postMessage({
            type: "contentChanged",
            payload: { markdown: editor.storage.markdown.getMarkdown() },
        });
    },
});

// Expose API for Swift-to-JS commands
(window as any).editorAPI = {
    setContent: (md: string) => editor.commands.setContent(md),
    toggleBold: () => editor.chain().focus().toggleBold().run(),
    focus: () => editor.commands.focus(),
    // ... remaining commands
};
```

```javascript
// build-editor.mjs
import { build } from "esbuild";
await build({
    entryPoints: ["src/editor-standalone.ts"],
    bundle: true, minify: true,
    outfile: "EditorBundle/editor.js",
    format: "iife", target: ["safari17"],
});
```

Copy `EditorBundle/` into Xcode as a folder reference. Load with `loadFileURL`.

---

## NSViewRepresentable (macOS) and UIViewRepresentable (iOS)

```swift
// macOS
struct EditorWebView: NSViewRepresentable {
    let bridge: EditorBridge

    func makeNSView(context: Context) -> WKWebView {
        let config = EditorWebViewFactory.makeConfiguration(bridge: bridge)
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        EditorWebViewFactory.loadBundledEditor(into: webView)
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) { /* never reload */ }
    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            decisionHandler(action.navigationType == .linkActivated ? .cancel : .allow)
        }
    }
}

// iOS — identical except UIViewRepresentable and makeUIView/updateUIView
struct EditorWebView: UIViewRepresentable {
    let bridge: EditorBridge
    func makeUIView(context: Context) -> WKWebView {
        let config = EditorWebViewFactory.makeConfiguration(bridge: bridge)
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.keyboardDismissMode = .interactive
        EditorWebViewFactory.loadBundledEditor(into: webView)
        return webView
    }
    func updateUIView(_ webView: WKWebView, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator() }
    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            decisionHandler(action.navigationType == .linkActivated ? .cancel : .allow)
        }
    }
}
```

---

## Division of Labor

| Responsibility | Owner | Why |
|---------------|-------|-----|
| Rich text editing | WebView (Tiptap) | Mature, extensible |
| Content storage | Swift (SwiftData) | Offline-first |
| API calls | Swift (actor) | Token management, auth |
| Navigation | Swift (NavigationStack) | Native feel, deep links |
| Theme / appearance | Both | Swift sets CSS vars via bridge |
| Keyboard shortcuts | Swift | Native menu bar integration |
| Link handling | Swift (via bridge) | SFSafariViewController |
| Slash commands | WebView detects, Swift fulfills | WebView captures `/`, Swift provides data |
| Search (across docs) | Swift (SwiftData queries) | Full local database |
| Undo/Redo | WebView (ProseMirror) | Editor owns history stack |
| Sync with server | Swift (SyncEngine) | Background, offline-aware |

---

## Anti-Patterns

**1. WebView making direct API calls** — Token lives in Keychain. Route all
API calls through the bridge: `sendToSwift("fetchNote", { id: "123" })`.

**2. Loading from remote URL** — Always bundle the editor. Remote loading adds
latency and breaks offline.

**3. Poor content escaping** — `"setContent('\(markdown)')"` breaks on backticks,
dollar signs, quotes. Always use `EditorCommand.escapeForJS()`.

**4. Recreating WebView on state change** — Never reload in `updateNSView`.
Reloading destroys undo history and cursor position. Send incremental commands.

**5. Completion-handler evaluateJavaScript** — Use `async/await` overload:
`try await webView.evaluateJavaScript(js)`.
