# Next-Pro Agent Registry

## Agent Selection

Agents are composable. A single task may load multiple agents.

### By Task Type

| Task | Primary Agent | Also Load | Key Refs |
|------|--------------|-----------|----------|
| Build a page or feature | `next-feature` | `next-data` (if fetching) | rendering-strategies.md |
| Data fetching / caching | `next-data` | | data-patterns.md, use-cache.md |
| Route structure design | `next-routing` | | route-conventions.md |
| SEO / metadata / OG images | `next-metadata` | | metadata.tsx |
| Middleware / redirects | `next-middleware` | | middleware-patterns.md |
| Error diagnosis | `next-triage` | (routes to specialist) | errors/*.mdx |
| Hydration mismatch | `next-hydration` | | hydration-patterns.md |
| RSC boundary error | `next-rsc` | | server-client-boundary.md |
| Build failure | `next-build` | `next-runtime` (if module) | build-pipeline.md |
| HMR / dev server | `next-devserver` | | dev server source |
| 404 / navigation bug | `next-debug-route` | | router-internals.md |
| Runtime / bundle / DCE | `next-runtime` | `next-build` | runtime-bundles.md |

### Multi-Agent Sessions

Common development combinations:

- **Full page build**: `next-feature` + `next-data` + `next-routing`
- **API route with auth**: `next-feature` + `next-middleware`
- **SEO-optimized page**: `next-feature` + `next-metadata` + `next-data`
- **Bug in new feature**: `next-feature` + `next-triage` (switch tracks)

Common diagnostic combinations:

- **Hydration + RSC boundary**: Component renders differently on server vs.
  client because of incorrect "use client" placement.
- **Build + Runtime**: Build succeeds but runtime crashes because a Node-only
  module was included in an edge bundle.
- **Dev server + Routing**: Navigation works in production but fails in dev.
