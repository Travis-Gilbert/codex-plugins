# PWA Caching Strategies

> When to use which Workbox strategy, per route type.

## Strategy Reference

| Strategy | Behavior | Best For |
|----------|----------|----------|
| CacheFirst | Check cache, fall back to network | Static assets, fonts, content-hashed files |
| NetworkFirst | Try network, fall back to cache | API responses, dynamic HTML, RSC payloads |
| StaleWhileRevalidate | Return cache immediately, update in background | App shell HTML, semi-static content |
| NetworkOnly | Always network, never cache | POST/PUT/DELETE mutations, auth endpoints |
| CacheOnly | Always cache, never network | Precached app shell, offline fallback page |

## Next.js App Router Route Map

| Route Pattern | Strategy | Rationale |
|---------------|----------|-----------|
| `/_next/static/**` | CacheFirst | Content-hashed immutable bundles |
| `/_next/image/**` | CacheFirst | Optimized images with cache busting via URL |
| `/api/**` (GET) | NetworkFirst | Fresh data preferred, cache for offline |
| `/api/**` (POST) | NetworkOnly + BackgroundSync | Never cache mutations; queue when offline |
| `/_next/data/**` (RSC) | NetworkFirst | Server-rendered payloads, must not serve stale |
| `/` and page routes | StaleWhileRevalidate | Fast paint from cache, update in background |
| `/fonts/**` | CacheFirst | Rarely change, expensive to re-fetch |
| Third-party CDN | StaleWhileRevalidate | Balance freshness with speed |

## Service Worker Lifecycle

1. **Install**: Precache app shell and critical assets
2. **Waiting**: New SW waits until all tabs close (or skipWaiting)
3. **Activate**: Clean old caches, claim clients
4. **Fetch**: Route-matching applies strategies above

### skipWaiting Trade-off

- `skipWaiting()`: New SW activates immediately. Risk: in-flight requests
  may get mismatched assets (old HTML referencing new JS chunks).
- Without skipWaiting: Safer but requires user to close all tabs for update.
- **Recommendation**: Use skipWaiting with a "New version available" prompt
  that triggers `window.location.reload()` on user action.

## Cache Versioning

Use Workbox's `CacheableResponsePlugin` with `statuses: [0, 200]` to
avoid caching error responses. Set `maxEntries` and `maxAgeSeconds` per
cache to prevent unbounded growth:

- Static assets: maxEntries 200, no expiry (content-hashed)
- API responses: maxEntries 50, maxAgeSeconds 86400 (1 day)
- Images: maxEntries 100, maxAgeSeconds 604800 (7 days)

## Serwist Integration (Next.js)

Serwist is the maintained successor to next-pwa. Integration:

1. `npm install @serwist/next @serwist/sw`
2. Wrap next.config with `withSerwist({ swSrc: "app/sw.ts", swDest: "public/sw.js" })`
3. Write `app/sw.ts` importing strategies from `@serwist/sw`
4. Add `<link rel="manifest" href="/manifest.webmanifest" />` or use `app/manifest.ts`
