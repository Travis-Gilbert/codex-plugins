# Component APIs

> Link, Image, Script, Form, Font, and next/dynamic.
>
> **Source files**: link.tsx (23K), image-component.tsx (13K),
> script.tsx (11K), form.tsx, dynamic.tsx

## Link

Prefetch behavior, scroll restoration, active state detection.

<!-- TODO: Populate from refs/next-client/link.tsx -->

## Image

Loader system, responsive sizes, priority loading, blur placeholder.

<!-- TODO: Populate from refs/next-client/image-component.tsx -->

## Script

Loading strategies:
- `beforeInteractive` — load before page hydrates
- `afterInteractive` — load after page hydrates (default)
- `lazyOnload` — load during idle time
- `worker` — load in web worker (experimental)

<!-- TODO: Populate from refs/next-client/script.tsx -->

## Form

Progressive enhancement, action attribute, method handling.

<!-- TODO: Populate from refs/next-client/form.tsx -->

## next/dynamic

SSR control, loading component, no-SSR pattern:
```tsx
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('./Chart'), {
  ssr: false,
  loading: () => <p>Loading chart...</p>,
})
```

<!-- TODO: Populate from refs/next-shared/dynamic.tsx -->
