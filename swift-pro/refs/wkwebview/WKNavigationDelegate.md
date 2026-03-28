# WKNavigationDelegate Reference

> Navigation handling, URL interception, and file loading for WKWebView.

## Protocol Methods

```swift
protocol WKNavigationDelegate: NSObjectProtocol {
    // Decide whether to allow navigation
    func webView(_ webView: WKWebView,
                 decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void)

    // Called when navigation starts
    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!)

    // Called when content starts loading
    func webView(_ webView: WKWebView, didCommit navigation: WKNavigation!)

    // Called when navigation completes
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!)

    // Called on navigation error
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error)

    // Called on provisional navigation error (before commit)
    func webView(_ webView: WKWebView,
                 didFailProvisionalNavigation navigation: WKNavigation!,
                 withError error: Error)
}
```

## URL Interception (for link handling)

```swift
func webView(
    _ webView: WKWebView,
    decidePolicyFor navigationAction: WKNavigationAction,
    decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
) {
    guard let url = navigationAction.request.url else {
        decisionHandler(.allow)
        return
    }

    // Allow local file loading (bundled editor)
    if url.isFileURL {
        decisionHandler(.allow)
        return
    }

    // Intercept external links — open in system browser
    if url.scheme == "https" || url.scheme == "http" {
        NSWorkspace.shared.open(url)  // macOS
        // UIApplication.shared.open(url)  // iOS
        decisionHandler(.cancel)
        return
    }

    // Intercept custom scheme (e.g., studio://navigate/object/123)
    if url.scheme == "studio" {
        handleCustomScheme(url)
        decisionHandler(.cancel)
        return
    }

    decisionHandler(.allow)
}
```

## Page Load Completion

```swift
func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
    // Editor HTML is fully loaded — safe to send initial content
    if let content = pendingContent {
        sendCommand(.loadContent(markdown: content))
        pendingContent = nil
    }
}
```

## Error Handling

```swift
func webView(
    _ webView: WKWebView,
    didFailProvisionalNavigation navigation: WKNavigation!,
    withError error: Error
) {
    let nsError = error as NSError

    // Ignore cancelled navigation (user navigated away)
    if nsError.code == NSURLErrorCancelled { return }

    // Log actual errors
    print("WebView load failed: \(error.localizedDescription)")
}
```

## Common Patterns

- **Always intercept external links** — don't let the WebView navigate away from the editor
- **Use `didFinish` to know when to send initial content** — evaluateJavaScript before page load will fail silently
- **Custom URL schemes** for in-app navigation (e.g., wiki links, deep links)
- **`allowingReadAccessTo`** is set during `loadFileURL`, not in the delegate
