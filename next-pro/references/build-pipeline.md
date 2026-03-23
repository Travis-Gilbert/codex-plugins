# Build Pipeline

> How `next build` works from entry to output. The build agent's
> primary reference.
>
> **Source files**: index.ts, entries.ts, webpack-config.ts, define-env.ts,
> handle-externals.ts, create-compiler-aliases.ts, compiler.ts,
> print-build-errors.ts, type-check.ts, validate-app-paths.ts,
> route-bundle-stats.ts, config.ts, config-shared.ts, config-schema.ts

## Build Phases (from index.ts)

1. Config loading and validation
2. TypeScript checking
3. Route discovery and validation
4. Entry point determination
5. Compilation (webpack or turbopack)
6. Static generation / prerendering
7. Output and manifest writing

<!-- TODO: Populate phase details from refs/next-build/index.ts -->

## Config Loading

`config.ts` loads the config, `config-schema.ts` validates with zod.

<!-- TODO: Populate from refs/next-server/config.ts, config-schema.ts -->

## Entry Point Classification

`entries.ts` determines what to compile — server vs. client entries.

<!-- TODO: Populate from refs/next-build/entries.ts -->

## Webpack Configuration

Key sections of `webpack-config.ts`: aliases, externals, plugins, define-env.

<!-- TODO: Populate key sections from refs/next-build/webpack-config.ts -->

## Module Resolution

`handle-externals.ts` decides bundle vs. externalize.
`create-compiler-aliases.ts` sets up path aliases.

<!-- TODO: Populate from refs/next-build/handle-externals.ts -->

## Build-Time Replacements (define-env.ts)

`process.env.X` values replaced at build time. Does NOT affect
pre-compiled runtime bundles.

<!-- TODO: Populate from refs/next-build/define-env.ts -->

## Static Generation

How pages are prerendered, what triggers dynamic bailout.

<!-- TODO: Populate from refs/next-server/app-render/dynamic-rendering.ts -->

## Error Surfacing

`print-build-errors.ts` formats and displays errors to the user.

<!-- TODO: Populate from refs/next-build/print-build-errors.ts -->

## Common Build Failure Patterns

- Config validation (misspelled keys, wrong types)
- Module resolution (Node built-ins in edge/client)
- Static generation (dynamic APIs without Suspense)
- TypeScript errors in route segments
