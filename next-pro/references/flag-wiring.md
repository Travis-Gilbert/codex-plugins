# Feature Flag Wiring

> How to trace feature flags end-to-end.
>
> **Source files**: config-shared.ts, config-schema.ts, define-env.ts,
> next-server.ts

## Required Wiring

Every feature flag must appear in at minimum:
1. `config-shared.ts` — TypeScript type declaration
2. `config-schema.ts` — Zod validation schema

## Client/Bundled Code Only

If the flag is consumed only in user-bundled code (client components,
server components compiled by the user's bundler):
- Add to `define-env.ts` — this injects the value at build time

## Pre-Compiled Runtime Bundles

If the flag is consumed in pre-compiled runtime code (app-render.tsx,
route modules, etc.):
- `define-env.ts` alone is NOT sufficient
- Need real `process.env` at runtime
- Two approaches:
  1. Runtime env var setup in `next-server.ts`
  2. Separate bundle variant (for performance-critical paths)

## Runtime Bundle Model

The pre-compiled bundles are built by:
- `next-runtime.webpack-config.js` — webpack config for runtime bundles
- `taskfile.js` — build orchestrator
- `module.compiled.js` — runtime variant selector

## Common Debugging Pattern

User reports config option "not working":

1. **Is the flag in config-shared.ts?** If not, it's not a valid option.
2. **Is it in config-schema.ts?** If not, it won't pass validation.
3. **Is it in define-env.ts?** If not, user-bundled code can't see it.
4. **Is it consumed in pre-compiled code?** If yes, is there runtime
   env setup? Without it, the pre-compiled code gets `undefined`.
5. **Is it forced false for edge?** If consumed with Node.js APIs,
   must be `isEdgeServer ? false : value` in define-env.ts.
