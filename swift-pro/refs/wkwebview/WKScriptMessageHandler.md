# WKScriptMessageHandler Reference

> JS-to-Swift message passing via WKScriptMessageHandler.

## Protocol

```swift
protocol WKScriptMessageHandler: NSObjectProtocol {
    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage
    )
}
```

## Registration

```swift
// Register handler with a name
config.userContentController.add(handler, name: "studio")

// JS can now call:
// window.webkit.messageHandlers.studio.postMessage({ type: "save", data: "..." })
```

## WKScriptMessage Properties

```swift
func userContentController(
    _ controller: WKUserContentController,
    didReceive message: WKScriptMessage
) {
    message.name        // "studio" — the handler name
    message.body        // Any — the JS value passed to postMessage()
    message.frameInfo   // Info about the frame that sent the message
    message.webView     // The WKWebView that sent it (weak)
}
```

## Message Body Types

The `body` property maps JS types to Swift:

| JS Type | Swift Type |
|---------|-----------|
| `string` | `String` |
| `number` | `NSNumber` (Int or Double) |
| `boolean` | `NSNumber` (0 or 1) |
| `object` | `[String: Any]` (dictionary) |
| `array` | `[Any]` |
| `null` | `NSNull` |
| `undefined` | Not sent (postMessage fails) |

## Typed Message Routing Pattern

```swift
final class EditorBridge: NSObject, WKScriptMessageHandler {
    weak var coordinator: EditorCoordinator?

    func userContentController(
        _ controller: WKUserContentController,
        didReceive message: WKScriptMessage
    ) {
        guard let body = message.body as? [String: Any],
              let type = body["type"] as? String else {
            return  // Silently ignore malformed messages
        }

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
            break  // Unknown message types are silently ignored
        }
    }
}
```

## Memory Management

**Important**: `WKUserContentController` retains its message handlers
strongly. To avoid retain cycles:

```swift
// Remove handler when done (e.g., in deinit or viewWillDisappear)
webView.configuration.userContentController.removeScriptMessageHandler(forName: "studio")
```

Or use `WKScriptMessageHandlerWithReply` (iOS 14+) for request/response
patterns where the handler can return a value to JS.

## JS Side

```javascript
// Send message to Swift
window.webkit.messageHandlers.studio.postMessage({
    type: 'contentChanged',
    markdown: editor.getMarkdown(),
    wordCount: 1234,
});

// Check if bridge is available (defensive)
if (window.webkit?.messageHandlers?.studio) {
    window.webkit.messageHandlers.studio.postMessage({ type: 'ready' });
}
```
