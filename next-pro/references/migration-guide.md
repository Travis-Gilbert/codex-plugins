# Migration Guide

> Breaking changes across Next.js versions.
>
> **Source files**: params.ts, search-params.ts, patch-fetch.ts

## v14 to v15

### Async Request APIs (Breaking)

In Next.js 15, `params`, `searchParams`, `cookies()`, and `headers()`
are all async / Promise-based:

```tsx
// Before (v14)
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>
}

// After (v15)
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <div>{id}</div>
}
```

### Fetch No Longer Cached by Default (Breaking)

```tsx
// v14: cached by default
const data = await fetch(url)

// v15: NOT cached. Opt in:
const data = await fetch(url, { cache: 'force-cache' })
```

### Turbopack Default

Turbopack is the default bundler for both dev and build. Use `--webpack`
to opt out.

### React 19

Next.js 15 ships with React 19. Key changes:
- `ref` as a regular prop (no more forwardRef)
- `use()` hook for reading promises and context
- Actions and `useActionState` / `useFormStatus`

## v13 to v14

- Server Actions stable
- Turbopack stable for dev
- Partial Prerendering (experimental)

## Common Migration Pitfalls

- Forgetting to `await` params/searchParams (silent bug, returns Promise)
- Assuming fetch is cached (stale data in v15 without explicit caching)
- Using Node.js APIs in middleware/edge (moved to edge runtime)
