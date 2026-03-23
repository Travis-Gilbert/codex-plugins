# Offline Sync Protocol

> Read-path vs write-path offline, conflict resolution strategies.

## The Five Levels

| Level | Name | Complexity | Use When |
|-------|------|-----------|----------|
| 0 | Online-only | None | Auth, payments |
| 1 | Cache-and-show | Low | Read-only browsing |
| 2 | Stale-while-refresh | Low-Med | Feeds, dashboards |
| 3 | Optimistic writes | Medium | Simple creates (captures) |
| 4 | Queued writes | Med-High | Forms, edits that can fail |
| 5 | Bidirectional sync | High | Multi-device collaborative |

**Most apps need Level 2 for reading and Level 3 for capture.**

## Read-Path Offline (Levels 1-2)

### TanStack Query Persistence

```typescript
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV();
const persister = createSyncStoragePersister({
  storage: {
    getItem: (key) => storage.getString(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: (key) => storage.delete(key),
  },
});

persistQueryClient({ queryClient, persister, maxAge: 1000 * 60 * 60 * 24 });
```

### ETag-Based Refresh

```
GET /api/v1/objects/my-slug/
If-None-Match: "abc123"

→ 304 Not Modified (no body, save bandwidth)
→ 200 OK + new ETag (data changed)
```

## Write-Path Offline (Levels 3-4)

### Mutation Queue

```typescript
interface QueuedMutation {
  id: string;
  endpoint: string;
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body: Record<string, unknown>;
  timestamp: string;
  retries: number;
  status: 'pending' | 'syncing' | 'failed' | 'synced';
}
```

### Sync Manager

1. Queue mutations locally with client timestamps
2. On connectivity restore, replay in order
3. For each mutation: send to server, handle response
4. If conflict: mark mutation as `failed`, surface to user
5. If success: mark as `synced`, remove from queue

### Background Sync (PWA)

Workbox BackgroundSync queues failed POST/PUT requests in IndexedDB
and replays them when the ServiceWorkerRegistration's `sync` event fires.

## Conflict Resolution Strategies

| Data Pattern | Strategy | Server Implementation |
|-------------|----------|----------------------|
| Append-only | No conflict | Accept all, order by timestamp |
| Single-user edits | Last-write-wins | Compare `updated_at`, newer wins |
| Multi-user, mergeable | Field-level merge | Merge non-conflicting fields |
| Multi-user, non-mergeable | Manual resolution | Return both versions to client |
| Collaborative | CRDT/OT | Yjs or Automerge |

## Sync Endpoint Contracts

### Pull Sync

```
GET /api/v1/mobile/sync/?since=<ISO-timestamp>&tables=objects,edges

Response:
{
  "changes": {
    "objects": {
      "created": [...],
      "updated": [...],
      "deleted": ["id1", "id2"]
    }
  },
  "timestamp": "2025-03-23T08:30:00Z"
}
```

### Push Sync

```
POST /api/v1/mobile/sync/push/

{
  "changes": {
    "objects": { "created": [...], "updated": [...] }
  },
  "client_timestamp": "2025-03-23T08:25:00Z"
}

Response:
{
  "accepted": 12,
  "conflicts": [
    { "id": "obj_123", "server_version": {...}, "client_version": {...} }
  ],
  "server_timestamp": "2025-03-23T08:30:01Z"
}
```

## WatermelonDB Sync

WatermelonDB has a built-in sync protocol. The server must implement
a compatible endpoint. Grep `refs/watermelondb/src/sync/` for the
exact contract (pullChanges, pushChanges, migrationsEnabledAtVersion).
