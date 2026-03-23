# Data Patterns

> Fetching, caching, mutations, and revalidation patterns.
>
> **Source files**: patch-fetch.ts, response-cache/, action-handler.ts,
> cookies.ts, headers.ts

## Fetch Behavior in Next.js 15+

fetch() is NOT cached by default (changed from v14). Opt in explicitly:
- `cache: 'force-cache'` — cache indefinitely
- `next: { revalidate: N }` — cache with time-based revalidation
- `next: { tags: ['tag'] }` — cache with tag-based invalidation

<!-- TODO: Populate from refs/next-server/lib/patch-fetch.ts -->

## Four Cache Layers

1. **Router Cache** (client, in-memory) — 30s dynamic, 5min static
2. **Full Route Cache** (server, persisted) — static routes only
3. **Data Cache** (server, per-fetch) — opt-in in v15+
4. **Data Source** — database, API, etc.

## Revalidation

- `revalidatePath()` — purges Data Cache + Full Route Cache
- `revalidateTag()` — purges tagged entries in Data Cache
- Neither purges client Router Cache directly

<!-- TODO: Populate from refs/next-server/response-cache/ -->

## Server Action Mutations

Actions throw on error (not return error objects). The pipeline:
parse -> validate -> execute -> revalidate -> respond.

<!-- TODO: Populate from refs/next-server/app-render/action-handler.ts -->
