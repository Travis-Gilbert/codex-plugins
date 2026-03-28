# WKWebViewConfiguration Reference

> Configuration, user content controller, and preferences for WKWebView.

## Basic Configuration

```swift
let config = WKWebViewConfiguration()

// User content controller for JS bridge
let contentController = WKUserContentController()
contentController.add(bridge, name: "studio")  // JS: window.webkit.messageHandlers.studio
config.userContentController = contentController

// Preferences
config.preferences.javaScriptCanOpenWindowsAutomatically = false

// Process pool (share across multiple WebViews for shared cookies/storage)
config.processPool = WKProcessPool()

// Data store (for cookies, local storage)
config.websiteDataStore = .default()  // Or .nonPersistent() for no storage

let webView = WKWebView(frame: .zero, configuration: config)
```

## User Scripts (inject JS before/after page load)

```swift
// Inject JS that runs before the page's own scripts
let earlyScript = WKUserScript(
    source: "window.isNativeApp = true; window.platform = 'macOS';",
    injectionTime: .atDocumentStart,
    forMainFrameOnly: true
)
contentController.addUserScript(earlyScript)

// Inject JS that runs after DOM is loaded
let lateScript = WKUserScript(
    source: "document.body.classList.add('native-app');",
    injectionTime: .atDocumentEnd,
    forMainFrameOnly: true
)
contentController.addUserScript(lateScript)
```

## Key Properties

- `userContentController` — Bridge between JS and Swift
- `preferences` — JS settings, minimum font size
- `processPool` — Share process across WebViews
- `websiteDataStore` — Cookie and storage persistence
- `allowsInlineMediaPlayback` — Play media inline (iOS)
- `mediaTypesRequiringUserActionForPlayback` — Autoplay policy
- `applicationNameForUserAgent` — Custom user agent suffix

## Loading Bundled Content

```swift
// Load HTML from app bundle
if let url = Bundle.main.url(
    forResource: "editor",
    withExtension: "html",
    subdirectory: "EditorBundle"
) {
    // allowingReadAccessTo: lets the HTML load sibling CSS/JS files
    webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
}
```

**Critical**: Without `allowingReadAccessTo`, the HTML file loads but
cannot access CSS, JS, fonts, or images in the same directory.
