# Runtime Bundles

> How Next.js pre-compiles and selects between multiple runtime
> bundle variants. The runtime inspector agent's primary reference.
>
> **Source files**: route-modules/app-page/, config-shared.ts,
> define-env.ts, next-server.ts, entry-base.ts

## Bundle Variant Model

Next.js pre-compiles multiple runtime variants:
`{turbo/webpack} x {experimental/stable/nodestreams} x {dev/prod}`

These variants are built ahead of time and shipped with the framework.

<!-- TODO: Populate variant count and build process -->

## Bundle Selection

`module.compiled.js` in `route-modules/app-page/` selects the
correct variant at runtime based on environment variables.

<!-- TODO: Populate from refs/next-server/route-modules/app-page/ -->

## define-env.ts vs Runtime Env Vars

**Critical distinction**: `define-env.ts` affects USER bundling
(the application's webpack/turbopack build), NOT the pre-compiled
runtime bundles. `process.env` references in `app-render.tsx` are
either replaced by DefinePlugin at runtime-bundle-build time, or
read as actual environment variables at server startup.

## Flag Wiring End-to-End

```
config-shared.ts (TypeScript type)
  -> config-schema.ts (zod validation)
    -> define-env.ts (build-time injection for user code)
      -> runtime (real process.env for pre-compiled code)
```

## Adding a New Flag

1. Add type to `config-shared.ts`
2. Add zod validation to `config-schema.ts`
3. Add to `define-env.ts` if consumed in user-bundled code
4. Add runtime env setup if consumed in pre-compiled code

## Diagnosing Wrong Bundle

**Symptoms**: Bizarre errors, features not activating, wrong React channel
**Verification**: Check module.compiled.js selection, verify env vars
**Fix**: Ensure env vars match expected values for the target variant

## Bundle Tracing

Enable webpack stats to prove what's included:
```javascript
module.exports = { webpack(config) { config.profile = true; return config } }
```
