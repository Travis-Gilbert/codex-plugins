# React Vendoring

> How React is vendored in Next.js, the entry-base boundary, and
> implications for debugging.
>
> **Source files**: entry-base.ts, create-compiler-aliases.ts

## App Router: Vendored React

React is NOT resolved from `node_modules` for App Router pages.
It is vendored into `packages/next/src/compiled/` with two channels:
- **stable**: Default React build
- **experimental**: React with experimental features (PPR, etc.)

The channel is selected based on `next.config.js` experimental flags.

## The entry-base.ts Boundary

`entry-base.ts` is the ONLY file compiled in the `react-server` layer.
All `react-server-dom-webpack/*` imports MUST go through this file.

Other files access React server APIs via the `ComponentMod` pattern:
```typescript
// Don't do this:
import { renderToReadableStream } from 'react-server-dom-webpack/server'

// Do this:
const { renderToReadableStream } = ComponentMod
```

<!-- TODO: Populate from refs/next-server/app-render/entry-base.ts -->

## Adding Node.js-Only React APIs

1. Add types to the type definition
2. Export from `entry-base.ts`
3. Access via `ComponentMod` elsewhere

## The Turbopack Remap

Turbopack silently remaps all `react-server-dom-webpack/*` imports to
`react-server-dom-turbopack/*` via its import map. This means:
- Stack traces show `react-server-dom-turbopack` (this is normal)
- Error messages reference the turbopack variant
- The actual APIs are identical

## ESLint Patterns

Use scoped disable/enable for guarded requires in pre-compiled code:
```javascript
// eslint-disable-next-line @typescript-eslint/no-require-imports
const mod = require('react-server-dom-webpack/server')
```

## Debugging Implications

- Errors mentioning `react-server-dom-turbopack` = normal (Turbopack remap)
- Errors mentioning "react-server condition" = check `entry-base.ts`
- `Cannot find module 'react-server-dom-webpack'` = import not going through entry-base
