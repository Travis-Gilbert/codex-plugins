# PWA Setup for Next.js App Router

## Manifest

```typescript
// app/manifest.ts
import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'App Name',
    short_name: 'App',
    description: 'App description',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [
      { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
      { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
    ],
    screenshots: [
      { src: '/screenshots/desktop.png', sizes: '1920x1080', type: 'image/png', form_factor: 'wide' },
      { src: '/screenshots/mobile.png', sizes: '750x1334', type: 'image/png', form_factor: 'narrow' },
    ],
  };
}
```

### Icon Requirements for Installability
- 192x192 PNG (required)
- 512x512 PNG (required)
- 512x512 maskable PNG (recommended for Android)
- Screenshots improve the install prompt UI

## Service Worker Registration with Serwist

Serwist is the maintained successor to next-pwa. It provides first-class
Next.js App Router integration.

### Installation

```bash
pnpm add @serwist/next
pnpm add -D serwist
```

### Next.js Config

```typescript
// next.config.ts
import withSerwistInit from '@serwist/next';

const withSerwist = withSerwistInit({
  swSrc: 'app/sw.ts',
  swDest: 'public/sw.js',
});

export default withSerwist({
  // ... other Next.js config
});
```

### Service Worker

```typescript
// app/sw.ts
import { defaultCache } from '@serwist/next/worker';
import { Serwist } from 'serwist';

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: defaultCache,
});

serwist.addEventListeners();
```

## Custom Install Prompt

Browsers show a generic install prompt. Replace it with a branded experience:

```tsx
// components/InstallPrompt.tsx
'use client';

import { useEffect, useState } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setIsInstalled(true);
    }
    setDeferredPrompt(null);
  };

  if (isInstalled || !deferredPrompt) return null;

  return (
    <button
      onClick={handleInstall}
      className="fixed bottom-4 right-4 bg-primary text-primary-foreground px-4 py-2 rounded-lg shadow-lg"
    >
      Install App
    </button>
  );
}
```

## Offline Fallback Page

When the user navigates to a page that isn't cached while offline:

```tsx
// app/offline/page.tsx
export default function OfflinePage() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center space-y-4">
        <div className="text-6xl">📡</div>
        <h1 className="text-2xl font-bold">You're offline</h1>
        <p className="text-muted-foreground">
          Check your internet connection and try again.
        </p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-primary text-primary-foreground rounded"
        >
          Retry
        </button>
      </div>
    </div>
  );
}
```

Configure the service worker to serve this page for failed navigations:

```typescript
// In sw.ts, add offline fallback
import { NavigationRoute } from 'workbox-routing';
import { NetworkOnly } from 'workbox-strategies';

const navigationRoute = new NavigationRoute(
  new NetworkOnly(),
  { allowlist: [/^\/(?!api\/).*/] }
);
// Register with offline fallback URL
```

## Push Notification Registration

```typescript
// lib/push-registration.ts
export async function registerPushSubscription(vapidPublicKey: string) {
  const registration = await navigator.serviceWorker.ready;

  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
  });

  // Send subscription to backend
  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription),
  });

  return subscription;
}

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
```
