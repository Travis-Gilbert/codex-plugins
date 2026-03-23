# Next-Pro

A Claude Code plugin for building and debugging Next.js applications. Two tracks: **Development** for source-verified feature implementation, **Diagnostic** for error tracing through the framework's actual source code.

## What This Does

**Development Track**: When building features, Claude Code verifies APIs against the actual Next.js source — params are Promises in v15, fetch isn't cached by default, Server Actions have specific serialization rules. No more guessing from training data.

**Diagnostic Track**: When you report an error, Claude Code searches the complete error catalog (231 MDX files), greps the source to trace WHY the error occurs, and routes to a specialist agent.

## Agents

### Development Track

| Agent | Domain |
|-------|--------|
| next-feature | Pages, layouts, components, server actions |
| next-data | Data fetching, caching, mutations, revalidation |
| next-routing | Route design, parallel/intercepting routes |
| next-metadata | SEO, Open Graph, sitemaps, fonts |
| next-middleware | Middleware, edge functions, auth guards |

### Diagnostic Track

| Agent | Domain |
|-------|--------|
| next-triage | Error identification and routing |
| next-hydration | Server/client HTML divergence |
| next-rsc | "use client" / "use server" boundary errors |
| next-build | `next build` failures |
| next-devserver | HMR, Fast Refresh, dev overlay |
| next-debug-route | 404s, navigation, parallel routes |
| next-runtime | Bundle selection, DCE, edge runtime |

## Installation

### 1. Install the plugin

Add to your Claude Code plugins via `sync-plugins.sh`.

### 2. Populate source references

```bash
cd next-pro && bash install.sh
```

### 3. Pin to a specific version (optional)

```bash
bash install.sh . v15.2.0
```

## Supersedes

JS-Pro's `/nextjs` agent. After this plugin ships, JS-Pro routes all Next.js work here.
