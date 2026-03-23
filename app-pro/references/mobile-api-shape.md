# Mobile API Shape

> Token auth, cursor pagination, sparse fields, composite endpoints.

## Token Auth (SimpleJWT)

### Configuration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Endpoints

```
POST /api/token/          → {access, refresh}
POST /api/token/refresh/  → {access}
POST /api/token/verify/   → 200 or 401
```

### Mobile Client Pattern

Store refresh token in SecureStore (encrypted). Store access token
in memory only. Intercept 401 responses, refresh, retry original request.

## Cursor Pagination

### Why Not Offset?

Offset pagination breaks when items are inserted/deleted between pages.
User sees duplicate or missing items. Cursor pagination uses opaque
tokens that mark position in an ordered set.

### DRF Configuration

```python
class MobilePagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'
    cursor_query_param = 'cursor'
```

### Response Shape

```json
{
  "next": "https://api.example.com/objects/?cursor=cD0yMDI1LTAz",
  "previous": null,
  "results": [...]
}
```

## Sparse Fieldsets

### Query Parameter Pattern

```
GET /api/v1/objects/?fields=id,title,object_type,created_at
```

### DRF Mixin

```python
class SparseFieldsMixin:
    def get_fields(self):
        fields = super().get_fields()
        requested = self.context['request'].query_params.get('fields')
        if requested:
            allowed = set(requested.split(','))
            return {k: v for k, v in fields.items() if k in allowed}
        return fields
```

## Composite Endpoints

### Home Screen

```
GET /api/v1/mobile/home/

{
  "recent_objects": [...top 5 by updated_at...],
  "active_threads": [...],
  "notification_count": 7,
  "sync_pending": false,
  "last_sync": "2025-03-23T08:30:00Z"
}
```

### Local Graph (for offline cache)

```
GET /api/v1/mobile/graph/local/my-object-slug/?depth=2

{
  "root": {...object...},
  "edges": [...all edges within 2 hops...],
  "connected_objects": [...all objects within 2 hops...]
}
```

## Rate Limiting

Mobile clients should have separate throttle classes:

```python
class MobileUserRateThrottle(UserRateThrottle):
    rate = '100/minute'

class MobileBurstThrottle(UserRateThrottle):
    rate = '10/second'
```

## Versioning

Mobile apps cannot force-update like web apps. Use URL path versioning:

```
/api/v1/objects/    # Current
/api/v2/objects/    # Future (when breaking changes needed)
```

Maintain v1 for at least 6 months after v2 ships. Older app versions
in the wild cannot update until the user visits the app store.
