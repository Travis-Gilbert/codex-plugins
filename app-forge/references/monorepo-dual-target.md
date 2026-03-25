# Monorepo for Web + Desktop Dual-Target Builds

## Why a Monorepo

A single codebase serves two targets:
- **Web**: Next.js with full SSR, deployed to Vercel
- **Desktop**: Next.js static export wrapped in Tauri

Shared packages (UI components, API client, utilities) live once and are used by both.

## Workspace Configuration

### pnpm Workspace

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### Root package.json

```json
{
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "lint": "turbo lint",
    "dev:web": "turbo dev --filter=web",
    "dev:desktop": "turbo dev --filter=desktop",
    "build:web": "turbo build --filter=web",
    "build:desktop": "turbo build --filter=desktop"
  },
  "devDependencies": {
    "turbo": "^2"
  }
}
```

### Turborepo Pipeline

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "out/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    }
  }
}
```

## Shared Package Structure

### packages/ui — Shared Components

```json
// packages/ui/package.json
{
  "name": "@app/ui",
  "version": "0.0.0",
  "private": true,
  "exports": {
    ".": "./src/index.ts",
    "./*": "./src/*.tsx"
  },
  "dependencies": {
    "react": "^19"
  },
  "devDependencies": {
    "typescript": "^5"
  }
}
```

Components in `packages/ui/src/` are pure client components with no server dependencies. Both web and desktop apps import them.

### packages/api-client — Shared Fetch Wrappers

```typescript
// packages/api-client/src/client.ts
export class APIClient {
  constructor(private baseUrl: string, private getToken: () => string | null) {}

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: this.authHeaders(),
    });
    if (!res.ok) throw new APIError(res.status, await res.text());
    return res.json();
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { ...this.authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new APIError(res.status, await res.text());
    return res.json();
  }

  private authHeaders(): HeadersInit {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}
```

Both apps use the same API client. The web app might also use Server Components to fetch data directly — the API client is for client-side fetching.

### packages/shared — Utils, Validation, Constants

```typescript
// packages/shared/src/validation.ts
export const objectSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string(),
  type: z.enum(['essay', 'field-note', 'project']),
});

// packages/shared/src/constants.ts
export const SYNC_INTERVAL = 30_000; // 30 seconds
export const MAX_RECENT_ITEMS = 10;
```

## Per-App Configuration

### Web App (Full SSR)

```typescript
// apps/web/next.config.ts
import type { NextConfig } from 'next';

const config: NextConfig = {
  transpilePackages: ['@app/ui', '@app/api-client', '@app/shared'],
};

export default config;
```

### Desktop App (Static Export)

```typescript
// apps/desktop/next.config.ts
import type { NextConfig } from 'next';

const config: NextConfig = {
  output: 'export',
  images: { unoptimized: true },
  transpilePackages: ['@app/ui', '@app/api-client', '@app/shared'],
};

export default config;
```

## Conditional Code Patterns

### Environment Detection

```typescript
// packages/shared/src/env.ts
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
}

export function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

export function isServer(): boolean {
  return typeof window === 'undefined';
}
```

### Conditional Feature Rendering

```tsx
// Using in components
import { isTauri } from '@app/shared/env';

function AppToolbar() {
  return (
    <div className="toolbar">
      <h1>App Name</h1>
      {/* Only show in browser, not in Tauri (Tauri has native menu) */}
      {!isTauri() && <BrowserMenuBar />}
    </div>
  );
}
```

### Platform-Specific Implementations

```typescript
// packages/api-client/src/storage.ts
import { isTauri } from '@app/shared/env';

export async function saveToken(token: string): Promise<void> {
  if (isTauri()) {
    // Use Tauri's secure store
    const { Store } = await import('@tauri-apps/plugin-store');
    const store = await Store.load('auth.dat');
    await store.set('token', token);
    await store.save();
  } else {
    // Use browser localStorage (or httpOnly cookie via API)
    localStorage.setItem('auth_token', token);
  }
}
```

## CI/CD Pipeline

```yaml
# .github/workflows/build.yml
name: Build
on: [push]

jobs:
  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install
      - run: pnpm build:web
      # Deploy to Vercel or other hosting

  desktop:
    strategy:
      matrix:
        platform: [macos-latest, ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install
      - run: pnpm build:desktop
      # Produces platform-specific installers
```

## Dependency Management

- Shared dependencies (React, TypeScript) go in the root or shared packages
- App-specific dependencies go in the app's package.json
- Tauri dependencies go in `apps/desktop/package.json` and `apps/desktop/src-tauri/Cargo.toml`
- Use `pnpm add -w` for workspace-level dependencies
- Use `pnpm --filter desktop add` for app-specific dependencies
