# Debug Environment

> Every environment variable, debug flag, and diagnostic tool
> available for debugging Next.js applications.
>
> **Source files**: patch-error-inspect.ts, config-shared.ts,
> define-env.ts, next-dev-server.ts, log-requests.ts, debug-channel.ts

## Environment Variables

### Framework Debug

| Variable | Purpose | Where Defined |
|---|---|---|
| `DEBUG=next:*` | Enable all Next.js debug logging | debug module |
| `__NEXT_SHOW_IGNORE_LISTED=true` | Show full stack traces in dev | patch-error-inspect.ts |
| `NEXT_TELEMETRY_DISABLED=1` | Disable telemetry | telemetry module |

### Build Debug

| Variable | Purpose | Where Defined |
|---|---|---|
| `NEXT_SKIP_ISOLATE=1` | Skip packing for tests | build/index.ts |
| `IS_WEBPACK_TEST=1` | Force webpack in tests | test config |

### Test Debug

| Variable | Purpose | Where Defined |
|---|---|---|
| `NEXT_TEST_MODE=dev\|start` | Test in dev or production mode | test infrastructure |
| `HEADLESS=false` | Show browser in e2e tests | test config |

<!-- TODO: Complete from refs/next-build/define-env.ts -->

## Stack Trace Visibility

`patch-error-inspect.ts` controls stack trace filtering. By default,
internal Next.js frames are collapsed to "at ignore-listed frames".
Set `__NEXT_SHOW_IGNORE_LISTED=true` to see full traces.

<!-- TODO: Populate from refs/next-server/patch-error-inspect.ts -->

## Debug Logging

`DEBUG=next:*` enables all debug namespaces. Available namespaces
include request handling, routing, compilation, and rendering.

## DevTools

The Next.js DevTools provide error overlay, component inspection,
and performance monitoring in development mode.

<!-- TODO: Populate from refs/next-devtools/ -->

## Node.js Debugging

- `NODE_OPTIONS=--inspect` — attach debugger
- `NODE_OPTIONS=--cpu-prof` — CPU profiling
- V8 flags for JIT analysis

## Diagnostic Commands

- Webpack stats: `config.profile = true` in next.config.js
- Bundle analysis: check `route-bundle-stats.ts` output
- Route trace: inspect `.next/` manifest files
