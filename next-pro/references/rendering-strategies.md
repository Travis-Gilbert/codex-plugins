# Rendering Strategies

> Static, dynamic, ISR, PPR, and streaming — when Next.js chooses each
> and how to control it.
>
> **Source files**: dynamic-rendering.ts, staged-rendering.ts, stale-time.ts,
> app-render.tsx, segment-config/

## Static vs Dynamic

Next.js defaults to static rendering. A route becomes dynamic when it
uses request-specific APIs: `cookies()`, `headers()`, `searchParams`,
`connection()`, or uncached `fetch()`.

<!-- TODO: Populate exact conditions from refs/next-server/app-render/dynamic-rendering.ts -->

## ISR (Incremental Static Regeneration)

Time-based revalidation via `revalidate` export or `fetch({ next: { revalidate: N } })`.

## PPR (Partial Prerendering)

Experimental. Static shell served immediately, dynamic holes filled via
Suspense streaming. See `staged-rendering.ts`.

<!-- TODO: Populate from refs/next-server/app-render/staged-rendering.ts -->

## Streaming

Server components stream via ReadableStream. Suspense boundaries define
streaming segments.

## Stale Time

Router cache stale time defaults: 30s dynamic, 5min static.
See `stale-time.ts` for calculation.

<!-- TODO: Populate from refs/next-server/app-render/stale-time.ts -->

## Route Segment Config

```tsx
export const dynamic = 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = false | 0 | number
export const runtime = 'nodejs' | 'edge'
```
