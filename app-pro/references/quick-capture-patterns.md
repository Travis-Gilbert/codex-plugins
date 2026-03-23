# Quick Capture Patterns

> Share targets, widgets, deep links, offline queue.

## Design Principle

5-second ceiling: from "I have an idea" to "it is saved."

## Capture Flow

```
1. Entry point (share sheet / widget / notification / app icon)
      ↓
2. Single text input, pre-focused, keyboard open
      ↓
3. Optional: object type selector (defaults to last used)
      ↓
4. Optional: "connect to" (recent objects as suggestions)
      ↓
5. Tap save → immediate confirmation → background sync
```

## Entry Points

### Web Share Target (PWA)

Register in manifest:
```json
{
  "share_target": {
    "action": "/capture",
    "method": "POST",
    "enctype": "multipart/form-data",
    "params": {
      "title": "title",
      "text": "text",
      "url": "url"
    }
  }
}
```

Handle in service worker:
```javascript
self.addEventListener('fetch', (event) => {
  if (event.request.url.endsWith('/capture') && event.request.method === 'POST') {
    event.respondWith(handleShareTarget(event.request));
  }
});
```

### iOS Widget (WidgetKit)

```swift
struct CaptureWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "capture", provider: Provider()) { entry in
            Link(destination: URL(string: "myapp://capture")!) {
                Text("Quick Capture")
            }
        }
        .configurationDisplayName("Quick Capture")
        .supportedFamilies([.systemSmall])
    }
}
```

### Android App Widget

```xml
<appwidget-provider
    android:minWidth="40dp"
    android:minHeight="40dp"
    android:updatePeriodMillis="0"
    android:initialLayout="@layout/capture_widget" />
```

### Deep Link from Notification

```typescript
// Notification payload
{
  "title": "Capture this",
  "body": "You saved a link earlier",
  "data": {
    "type": "capture",
    "prefill": "The article about urban design",
    "connect_to": "urban-design-notebook"
  }
}

// Handle in app
Notifications.addNotificationResponseReceivedListener((response) => {
  const { type, prefill, connect_to } = response.notification.request.content.data;
  if (type === 'capture') {
    router.push(`/capture?prefill=${prefill}&connect=${connect_to}`);
  }
});
```

## Offline Capture Queue

```typescript
interface CaptureItem {
  id: string;            // Client-generated UUID
  content: string;
  object_type: string;
  connect_to_slug?: string;
  edge_type?: string;
  created_at: string;    // Client timestamp
  synced: boolean;
}

class CaptureQueue {
  private storage = new MMKV();

  add(item: Omit<CaptureItem, 'id' | 'created_at' | 'synced'>) {
    const capture: CaptureItem = {
      ...item,
      id: uuid(),
      created_at: new Date().toISOString(),
      synced: false,
    };
    const queue = this.getQueue();
    queue.push(capture);
    this.storage.set('capture_queue', JSON.stringify(queue));
    return capture;
  }

  async sync() {
    const pending = this.getQueue().filter(c => !c.synced);
    for (const item of pending) {
      try {
        await api.post('/mobile/capture/', item);
        this.markSynced(item.id);
      } catch (e) {
        if (isNetworkError(e)) break; // Stop, retry later
        this.markFailed(item.id);     // Server rejection
      }
    }
  }
}
```

## Backend Endpoint

```
POST /api/v1/mobile/capture/

{
  "content": "Jacobs argues that mixed-use neighborhoods...",
  "object_type": "claim",
  "connect_to_slug": "death-and-life-of-great-american-cities",
  "edge_type": "derived_from"
}

Response (201):
{
  "id": "obj_abc123",
  "slug": "jacobs-mixed-use-neighborhoods",
  "object_type": "claim",
  "created_at": "2025-03-23T14:22:00Z",
  "edge_created": true,
  "engine_passes_queued": true
}
```

The endpoint creates the Object synchronously, optionally creates an Edge,
and kicks engine passes to Celery asynchronously. The response includes
enough data for the client to display immediately.

## Conflict Strategy

Quick Capture is append-only (creating new records). No conflict
resolution needed. Last-write-wins is the implicit strategy, and it
works because each capture is a unique new object.
