# DCE and Edge Rules

> Dead code elimination patterns and edge runtime constraints.
>
> **Source files**: define-env.ts, entry-base.ts, stream-utils/,
> debug-channel-server.ts

## The DCE Rule

Webpack eliminates `require()` calls ONLY when they are in the dead
branch of an `if/else` whose condition DefinePlugin can statically
evaluate at compile time.

```javascript
// WORKS: webpack DCE eliminates the dead branch
if (process.env.__NEXT_USE_NODE_STREAMS) {
  require('node:stream')
} else {
  // web streams path
}

// BROKEN: early-return does NOT trigger DCE
if (!process.env.__NEXT_USE_NODE_STREAMS) return
require('node:stream')  // still traced by webpack!

// BROKEN: ternary require does NOT trigger DCE
const mod = process.env.FLAG ? require('a') : require('b')
// Both 'a' and 'b' are traced
```

## The Edge Constraint

Edge routes are compiled by the user's bundler (webpack/Turbopack),
not pre-compiled like the Node.js runtime. Feature flags that gate
`node:*` imports MUST be forced to `false` for edge builds:

```javascript
// In define-env.ts
isEdgeServer ? false : flagValue
```

## The Compile-Time Switcher Pattern

Use `.ts` switcher files that resolve to `.node.ts` or `.web.ts`:
```
stream-ops.ts       (switcher - imports the right one)
stream-ops.node.ts  (Node.js implementation)
stream-ops.web.ts   (Web Streams implementation)
```

<!-- TODO: Populate real examples from refs/next-server/stream-utils/ -->

## NEXT_RUNTIME Is Not a Feature Flag

Guarding on `process.env.NEXT_RUNTIME` does NOT prune Node-only code.
`NEXT_RUNTIME` is a runtime value, not a DefinePlugin replacement.
Use proper feature flags in `define-env.ts` instead.

## app-page.ts Template Gotchas

The build template uses `require()` which is traced by the bundler.
`entry-base.ts` exports are the only safe react-server layer surface.

## Verification

- Test with `next build` for both Node and edge targets
- Check webpack stats for unexpected module inclusion
- Verify `define-env.ts` forces flags false for edge
