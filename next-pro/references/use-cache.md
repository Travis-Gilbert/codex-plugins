# "use cache" Directive

> Experimental caching directive for Next.js 15+.
>
> **Source files**: use-cache-wrapper.ts (79K), cache-life.ts, cache-tag.ts

## Requirements

Requires `experimental.useCache: true` in next.config.js.

## How It Works

The "use cache" directive wraps a function's execution. When called:
1. Check if a cached result exists for the arguments
2. If yes, return cached result
3. If no, execute the function, cache the result, return it

<!-- TODO: Populate from refs/next-server/use-cache/use-cache-wrapper.ts -->

## cacheLife Profiles

Available presets for `cacheLife()`:
- `'seconds'` — short-lived cache
- `'minutes'` — medium cache
- `'hours'` — hourly refresh
- `'days'` — daily refresh
- `'weeks'` — weekly refresh
- `'max'` — cache as long as possible

<!-- TODO: Populate exact durations from refs/next-server/use-cache/cache-life.ts -->

## cacheTag

`cacheTag('tag-name')` enables targeted invalidation via `revalidateTag()`.

<!-- TODO: Populate from refs/next-server/use-cache/cache-tag.ts -->

## Serialization

Cached values must be serializable. Same rules as RSC boundary.

## Patterns

```tsx
async function getProducts() {
  'use cache'
  return db.products.findMany()
}

async function getProduct(id: string) {
  'use cache'
  cacheLife('hours')
  cacheTag(`product-${id}`)
  return db.products.findUnique({ where: { id } })
}
```
