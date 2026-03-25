# Background Sync Architecture

## The Three-Layer Background System

An app-like web experience coordinates three background systems. Each layer has a distinct responsibility:

| Layer | Technology | Responsibility | When Active |
|-------|-----------|---------------|-------------|
| 1 | Service Worker | Caching, offline, mutation queue | Always (installed) |
| 2 | Web Worker | Polling for new data | Tab open |
| 3 | Server-Sent Events | Real-time push from server | Tab open + online |

## Layer 1: Service Worker

### Route-Type Caching Strategies

```typescript
// sw.ts (using Serwist/Workbox)
import { CacheFirst, NetworkFirst, StaleWhileRevalidate, NetworkOnly } from 'workbox-strategies';
import { registerRoute } from 'workbox-routing';
import { BackgroundSyncPlugin } from 'workbox-background-sync';

// Static assets: cache forever (content-hashed filenames)
registerRoute(
  /\/_next\/static\/.*/,
  new CacheFirst({ cacheName: 'static-assets' })
);

// App shell HTML: fast load, background update
registerRoute(
  ({ request }) => request.mode === 'navigate',
  new StaleWhileRevalidate({ cacheName: 'app-shell' })
);

// API GET: prefer network, fall back to cache
registerRoute(
  /\/api\/v1\/.*$/,
  new NetworkFirst({
    cacheName: 'api-responses',
    networkTimeoutSeconds: 5,
  }),
  'GET'
);

// API mutations: never cache, queue for retry
const bgSyncPlugin = new BackgroundSyncPlugin('mutation-queue', {
  maxRetentionTime: 24 * 60, // 24 hours
});

registerRoute(
  /\/api\/v1\/.*$/,
  new NetworkOnly({ plugins: [bgSyncPlugin] }),
  'POST'
);
```

### Mutation Queue

Failed POST/PUT/PATCH/DELETE requests are queued by BackgroundSyncPlugin and replayed when connectivity returns. The queue persists in IndexedDB.

Important: Mutations in the queue must be idempotent or use server-side deduplication (request ID header).

```typescript
// Add request ID for deduplication
const originalFetch = self.fetch;
self.fetch = (input, init) => {
  if (init?.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(init.method)) {
    const headers = new Headers(init.headers);
    if (!headers.has('X-Request-ID')) {
      headers.set('X-Request-ID', crypto.randomUUID());
    }
    init.headers = headers;
  }
  return originalFetch(input, init);
};
```

## Layer 2: Web Worker (Polling)

### Worker Implementation

```typescript
// workers/data-poller.ts
interface PollConfig {
  apiUrl: string;
  token: string;
  pollInterval: number;  // ms
  endpoints: string[];   // API paths to poll
}

let interval: ReturnType<typeof setInterval>;

self.onmessage = (event: MessageEvent) => {
  const { type, config } = event.data;

  if (type === 'START') {
    startPolling(config as PollConfig);
  }

  if (type === 'STOP') {
    clearInterval(interval);
  }

  if (type === 'POLL_NOW') {
    poll(config as PollConfig);
  }
};

function startPolling(config: PollConfig) {
  clearInterval(interval);
  poll(config); // Immediate first poll
  interval = setInterval(() => poll(config), config.pollInterval);
}

async function poll(config: PollConfig) {
  for (const endpoint of config.endpoints) {
    try {
      const res = await fetch(`${config.apiUrl}${endpoint}`, {
        headers: { Authorization: `Bearer ${config.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        self.postMessage({ type: 'POLL_RESULT', endpoint, data });
      }
    } catch {
      self.postMessage({ type: 'POLL_ERROR', endpoint });
    }
  }
}
```

### Main Thread Integration

```typescript
// hooks/useDataPoller.ts
function useDataPoller(endpoints: string[], interval = 30000) {
  const workerRef = useRef<Worker | null>(null);

  useEffect(() => {
    const worker = new Worker(
      new URL('../workers/data-poller.ts', import.meta.url)
    );

    worker.onmessage = (event) => {
      if (event.data.type === 'POLL_RESULT') {
        // Update local state/cache with new data
        queryClient.setQueryData(
          [event.data.endpoint],
          event.data.data
        );
      }
    };

    worker.postMessage({
      type: 'START',
      config: { apiUrl: API_URL, token: getToken(), pollInterval: interval, endpoints },
    });

    workerRef.current = worker;
    return () => worker.terminate();
  }, [endpoints, interval]);

  return workerRef;
}
```

## Layer 3: Server-Sent Events

### Client Implementation

```typescript
// lib/sse-client.ts
class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map();

  connect(url: string, token: string) {
    this.eventSource = new EventSource(`${url}?token=${token}`);

    this.eventSource.onopen = () => {
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const handlers = this.listeners.get(data.type);
      handlers?.forEach(handler => handler(data));
    };

    this.eventSource.onerror = () => {
      this.eventSource?.close();
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000);
        this.reconnectAttempts++;
        setTimeout(() => this.connect(url, token), delay);
      }
    };
  }

  on(eventType: string, handler: (data: unknown) => void) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(handler);
  }

  off(eventType: string, handler: (data: unknown) => void) {
    this.listeners.get(eventType)?.delete(handler);
  }

  disconnect() {
    this.eventSource?.close();
    this.eventSource = null;
  }
}
```

## Coordination Between Layers

```
┌─────────────────────────────────────────┐
│  Tab Active + Online                     │
│  → SSE primary, Worker paused            │
│  → SW caches responses passively         │
├─────────────────────────────────────────┤
│  Tab Active + SSE Disconnected           │
│  → Worker resumes polling                │
│  → SW caches responses passively         │
├─────────────────────────────────────────┤
│  Tab Backgrounded                        │
│  → SSE disconnects (browser throttles)   │
│  → Worker continues (reduced interval)   │
│  → SW caches responses passively         │
├─────────────────────────────────────────┤
│  Offline                                 │
│  → SSE disconnected                      │
│  → Worker paused (fetch fails)           │
│  → SW serves cached content              │
│  → Mutations queued in IndexedDB         │
├─────────────────────────────────────────┤
│  Back Online                             │
│  → SW replays mutation queue             │
│  → SSE reconnects                        │
│  → Worker resumes (if SSE still down)    │
└─────────────────────────────────────────┘
```

## Sync Status UI

ALWAYS show sync status. The user must know three things:

1. **Connectivity**: online or offline
2. **Pending writes**: how many mutations are queued
3. **Freshness**: when data was last synced

```typescript
interface SyncState {
  isOnline: boolean;
  pendingMutations: number;
  lastSyncTimestamp: number | null;
  sseConnected: boolean;
}
```

## Notification Strategy

| Event | In-App | Browser Notification | OS Notification (Tauri) |
|-------|--------|---------------------|------------------------|
| New data available | Badge/dot update | No | No |
| Background task complete | Toast | If tab backgrounded | If app minimized |
| Sync conflict | Modal dialog | No | No |
| Back online after offline | Toast | No | No |
| Failed sync after retries | Persistent banner | Yes | Yes |
