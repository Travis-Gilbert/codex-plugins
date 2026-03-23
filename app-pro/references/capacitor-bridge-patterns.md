# Capacitor Bridge Patterns

> Static export, native plugins, server.url mode.

## Two Modes

### Bundled Mode (Static Export)

The Next.js app is exported as static files and bundled inside the
native shell. Works offline. No server required.

```typescript
// next.config.ts
export default {
  output: 'export',
  images: { unoptimized: true },
};
```

**Trade-offs**:
- Works offline
- No Server Components, Server Actions, or middleware
- No ISR/SSR
- All data fetching must be client-side

### Server URL Mode

Capacitor's WebView loads the hosted app. Full SSR, Server Components,
and Server Actions work. Requires network.

```typescript
// capacitor.config.ts
export default {
  server: {
    url: 'https://app.example.com',
    cleartext: false,
  },
};
```

**Trade-offs**:
- Full Next.js feature set
- Requires network connectivity
- Slower initial load (network round-trip)
- Can still access native plugins via Capacitor bridge

## Setup Checklist

1. `npm install @capacitor/core @capacitor/cli`
2. `npx cap init` (name, bundle ID)
3. `npm install @capacitor/ios @capacitor/android`
4. `npx cap add ios && npx cap add android`
5. Build: `npm run build` (or `next build && next export`)
6. Sync: `npx cap sync`
7. Open native project: `npx cap open ios` or `npx cap open android`

## Native Plugins

```typescript
import { Camera, CameraResultType } from '@capacitor/camera';
import { Filesystem, Directory } from '@capacitor/filesystem';
import { Share } from '@capacitor/share';

// Take photo
const photo = await Camera.getPhoto({
  resultType: CameraResultType.Uri,
  quality: 80,
});

// Save file
await Filesystem.writeFile({
  path: 'capture.txt',
  data: content,
  directory: Directory.Documents,
});

// Share
await Share.share({
  title: 'Check this out',
  text: 'Shared from my app',
  url: 'https://app.example.com/object/my-slug',
});
```

## Live Reload (Development)

```typescript
// capacitor.config.ts (dev only)
export default {
  server: {
    url: 'http://192.168.1.100:3000', // Local dev server IP
    cleartext: true, // Allow HTTP for development
  },
};
```

Remove or gate behind env variable for production builds.

## When to Graduate to React Native

Capacitor is the right choice when:
- The web UI already works well on mobile
- You need app store presence quickly
- You need 1-3 native APIs (camera, filesystem, push)
- The team does not have React Native experience

Graduate to React Native when:
- The mobile UX needs fundamentally different navigation
- Performance on WebView is insufficient (complex animations, heavy lists)
- You need deep native integration (background processing, widgets)
- The app needs to feel indistinguishable from native
