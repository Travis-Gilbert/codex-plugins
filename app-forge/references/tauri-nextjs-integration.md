# Tauri + Next.js Integration

## The Static Export Constraint

Tauri has no Node.js runtime. This is the single most important constraint.

### What Works in Tauri
- Static routes (`page.tsx` without server dependencies)
- Client Components (`'use client'`)
- Client-side `fetch()` to external APIs
- Dynamic routes with `generateStaticParams()` (pre-rendered at build)
- CSS Modules, Tailwind, CSS-in-JS
- All client-side JavaScript

### What Breaks in Tauri
- Server Components (no server to render on)
- Server Actions (no server to execute on)
- API routes (`app/api/`) (no server to handle requests)
- `getServerSideProps` / `getStaticProps` (Next.js Pages Router)
- `headers()`, `cookies()` server functions
- Database connections from the frontend
- Any `import 'server-only'` module

## Solution 1: Monorepo (Recommended)

### Workspace Structure

```
project/
├── apps/
│   ├── web/                        # Full Next.js with SSR
│   │   ├── next.config.ts          # Standard config
│   │   ├── app/                    # Can use Server Components
│   │   └── package.json
│   └── desktop/                    # Next.js static export for Tauri
│       ├── next.config.ts          # output: 'export'
│       ├── app/                    # Client components only
│       ├── src-tauri/              # Tauri Rust backend
│       └── package.json
├── packages/
│   ├── ui/                         # Shared React components
│   │   ├── src/
│   │   └── package.json
│   ├── api-client/                 # Shared fetch wrappers + types
│   │   ├── src/
│   │   └── package.json
│   └── shared/                     # Utils, validation, constants
│       ├── src/
│       └── package.json
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

### Desktop Next.js Config

```typescript
// apps/desktop/next.config.ts
import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,  // No image optimization server
  },
  // Tauri expects the output in 'out/'
  distDir: 'out',
};

export default config;
```

### Tauri Config

```json
// apps/desktop/src-tauri/tauri.conf.json
{
  "build": {
    "devUrl": "http://localhost:3001",
    "frontendDist": "../out"
  },
  "app": {
    "windows": [
      {
        "title": "App Name",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600
      }
    ]
  }
}
```

### Turborepo Pipeline

```json
// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "out/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### pnpm Workspace

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

## Solution 2: server.url Mode (Interim)

For apps that cannot yet split SSR from static export:

```json
// src-tauri/tauri.conf.json
{
  "build": {
    "devUrl": "http://localhost:3000",
    "frontendDist": {
      "url": "https://your-app.vercel.app"
    }
  }
}
```

The Tauri WebView loads the hosted web app. Native features (menus, tray, notifications) still work. But the app requires network access — it is not an offline-capable desktop app.

**When to use**: As a first step before building the full monorepo. Ship a desktop wrapper quickly, then migrate to static export later.

## SSR Guards for Tauri API Imports

Tauri's JavaScript API must never be imported during SSR:

```typescript
// lib/tauri-bridge.ts
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

export async function invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  if (typeof window === 'undefined') {
    throw new Error('Tauri invoke called during SSR');
  }
  const { invoke: tauriInvoke } = await import('@tauri-apps/api/core');
  return tauriInvoke<T>(cmd, args);
}
```

### Dynamic Import for Tauri Components

```tsx
// components/DesktopOnly.tsx
'use client';

import { useEffect, useState, type ReactNode } from 'react';

export function DesktopOnly({ children }: { children: ReactNode }) {
  const [isTauriEnv, setIsTauriEnv] = useState(false);

  useEffect(() => {
    setIsTauriEnv('__TAURI_INTERNALS__' in window);
  }, []);

  if (!isTauriEnv) return null;
  return <>{children}</>;
}
```

## Development Workflow

Run both Next.js dev server and Tauri dev server concurrently:

```json
// apps/desktop/package.json
{
  "scripts": {
    "dev": "next dev -p 3001",
    "dev:tauri": "tauri dev",
    "build": "next build",
    "build:tauri": "tauri build"
  }
}
```

```bash
# Terminal 1: Next.js dev server
pnpm --filter desktop dev

# Terminal 2: Tauri dev server (opens desktop window)
pnpm --filter desktop dev:tauri
```

## Production Build Pipeline

```bash
# 1. Build shared packages
pnpm --filter ui build
pnpm --filter api-client build

# 2. Build Next.js static export
pnpm --filter desktop build

# 3. Build Tauri app (reads from out/)
pnpm --filter desktop build:tauri
```

Output: platform-specific installers in `apps/desktop/src-tauri/target/release/bundle/`.
