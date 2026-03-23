# Router Internals

> How the App Router's client-side state machine works. The routing
> agent's primary reference.
>
> **Source files**: router.ts, app-router.tsx, layout-router.tsx,
> router-reducer/, segment-cache/, navigation.ts, links.ts, link.tsx,
> walk-tree-with-flight-router-state.tsx

## Two Routers

- **Pages Router**: `refs/next-shared/router/router.ts` (79K, legacy)
- **App Router**: `refs/next-client/components/app-router.tsx` (current)

## App Router State Machine

### State Shape

From `router-reducer-types.ts`: FlightRouterState, CacheNode,
ReadyCacheNode, PendingCacheNode.

<!-- TODO: Populate from refs/next-client/components/router-reducer/router-reducer-types.ts -->

### Initial State

From `create-initial-router-state.ts` — how the router bootstraps
from the server-rendered Flight data.

<!-- TODO: Populate from refs/next-client/components/router-reducer/create-initial-router-state.ts -->

### Actions

From `reducers/`: navigate, restore, refresh, prefetch, server-patch.

<!-- TODO: Populate from refs/next-client/components/router-reducer/reducers/ -->

## Navigation Flow

1. Link click or `useRouter.push()`
2. `fetch-server-response.ts` fetches Flight data from server
3. Router reducer applies the navigation action
4. `layout-router.tsx` re-renders affected segments only

## Prefetching

- Link prefetches on viewport entry (`links.ts`)
- Segment cache stores prefetched data (`cache.ts`, 111K)
- Scheduler prioritizes prefetches (`scheduler.ts`, 68K)

## PPR Navigations

`ppr-navigations.ts` handles partial prerendering during navigation.
The shell is served immediately, dynamic parts stream in.

<!-- TODO: Populate from refs/next-client/components/router-reducer/ppr-navigations.ts -->

## Segment Cache (New)

The segment cache replaces the old cache layer:
- `cache.ts` — core cache implementation
- `navigation.ts` — cache-aware navigation
- `scheduler.ts` — prefetch scheduling and prioritization

## Common Debugging Scenarios

- **Navigation doesn't update**: Check router reducer state, verify
  Flight data is fetched successfully
- **Prefetch data is stale**: Check segment cache TTL and eviction
- **Back/forward doesn't work**: Check restore action in reducer
- **Parallel route slots show wrong content**: Check default.tsx
  exports and slot resolution in create-component-tree.tsx
