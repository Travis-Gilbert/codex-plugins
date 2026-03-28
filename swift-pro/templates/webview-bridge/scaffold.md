# WebView Bridge Scaffold

> WKWebView wrapper + JS bridge + bundled editor for hybrid native/web apps.

## EditorBridge (Swift side receives JS messages)

```swift
import WebKit

final class EditorBridge: NSObject, WKScriptMessageHandler {
    weak var coordinator: EditorCoordinator?

    func userContentController(
        _ controller: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard let body = message.body as? [String: Any],
              let type = body["type"] as? String else { return }

        switch type {
        case "contentChanged":
            let markdown = body["markdown"] as? String ?? ""
            let wordCount = body["wordCount"] as? Int ?? 0
            coordinator?.handleContentChanged(markdown: markdown, wordCount: wordCount)
        case "saveRequested":
            coordinator?.handleSaveRequested()
        case "linkClicked":
            let url = body["url"] as? String ?? ""
            coordinator?.handleLinkClicked(url: url)
        case "ready":
            coordinator?.handleEditorReady()
        default:
            break
        }
    }
}
```

## EditorCommand (Swift side sends commands to JS)

```swift
enum EditorCommand {
    case loadContent(markdown: String)
    case getContent
    case focus
    case blur
    case setReadingSettings(json: String)

    var javascript: String {
        switch self {
        case .loadContent(let md):
            let escaped = md
                .replacingOccurrences(of: "\\", with: "\\\\")
                .replacingOccurrences(of: "`", with: "\\`")
                .replacingOccurrences(of: "$", with: "\\$")
            return "window.studioBridge.loadContent(`\(escaped)`)"
        case .getContent:
            return "window.studioBridge.getContent()"
        case .focus:
            return "window.studioBridge.focus()"
        case .blur:
            return "window.studioBridge.blur()"
        case .setReadingSettings(let json):
            return "window.studioBridge.setReadingSettings(\(json))"
        }
    }
}
```

## EditorWebView (macOS — NSViewRepresentable)

```swift
import SwiftUI
import WebKit

struct EditorWebView: NSViewRepresentable {
    let coordinator: EditorCoordinator

    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.userContentController.add(coordinator.bridge, name: "studio")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = coordinator
        coordinator.webView = webView

        if let url = Bundle.main.url(
            forResource: "editor", withExtension: "html",
            subdirectory: "EditorBundle"
        ) {
            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return webView
    }

    func updateNSView(_ nsView: WKWebView, context: Context) {}
}
```

## EditorWebView (iOS — UIViewRepresentable)

```swift
struct EditorWebView: UIViewRepresentable {
    let coordinator: EditorCoordinator

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.userContentController.add(coordinator.bridge, name: "studio")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = coordinator
        coordinator.webView = webView

        if let url = Bundle.main.url(
            forResource: "editor", withExtension: "html",
            subdirectory: "EditorBundle"
        ) {
            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
```

## Bundled Editor HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="editor.css">
    <style>
        body { margin: 0; padding: 16px; font-family: -apple-system, system-ui; }
        .ProseMirror { outline: none; min-height: 100vh; }
    </style>
</head>
<body>
    <div id="editor"></div>
    <script src="editor.js"></script>
    <script src="bridge.js"></script>
</body>
</html>
```

## Bridge JS (bridge.js)

```javascript
window.studioBridge = {
    loadContent(markdown) {
        // Called from Swift via evaluateJavaScript
        window.editor?.commands.setContent(markdown);
    },
    getContent() {
        return window.editor?.getMarkdown() ?? '';
    },
    focus() {
        window.editor?.commands.focus();
    },
    blur() {
        window.editor?.commands.blur();
    },
    setReadingSettings(settings) {
        // Apply font size, line height, etc.
        document.documentElement.style.setProperty('--font-size', settings.fontSize + 'px');
    }
};

// Notify Swift that editor is ready
if (window.webkit?.messageHandlers?.studio) {
    window.webkit.messageHandlers.studio.postMessage({ type: 'ready' });
}
```

## esbuild Extraction Script

```bash
#!/bin/bash
# extract-editor.sh
# Extract Tiptap editor from Next.js into standalone bundle

npx esbuild \
    src/components/editor/standalone-entry.tsx \
    --bundle \
    --format=iife \
    --outfile=EditorBundle/editor.js \
    --loader:.css=css \
    --external:react \
    --external:react-dom \
    --minify

# Copy CSS
cp src/styles/editor.css EditorBundle/editor.css

echo "Editor bundle extracted to EditorBundle/"
```
