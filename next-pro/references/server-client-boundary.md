# Server/Client Component Boundary

> The exact RSC serialization rules, what crosses the wire format,
> and how the boundary is enforced at build time and runtime.
>
> **Source files**: entry-base.ts, create-component-tree.tsx,
> use-flight-response.tsx, flight-data-helpers.ts, types.ts,
> entries.ts, error MDX files

## The Wire Format

React Server Components serialize via the Flight protocol. Server
components render to a stream of instructions that the client
interprets to build the component tree.

<!-- TODO: Populate from refs/next-server/app-render/use-flight-response.tsx -->

## What Can Cross

Serializable types: primitives, plain objects, arrays, Date, Server
Actions, JSX elements, Promises of serializable values.

## What Cannot Cross

Non-serializable: functions (except Server Actions), classes, Symbols,
closures, Node.js built-ins, React context, hooks, event handlers.

Each produces a specific error message documented in `errors/`.

## How the Boundary is Enforced

### Build-Time

`entries.ts` classifies modules into server and client entries.
The webpack/turbopack layer system enforces import restrictions.

<!-- TODO: Populate from refs/next-build/entries.ts -->

### Runtime

`entry-base.ts` is the ONLY file compiled in the react-server layer.
All `react-server-dom-webpack/*` imports must go through it.
`create-component-tree.tsx` resolves component types at render time.

<!-- TODO: Populate from refs/next-server/app-render/entry-base.ts -->

## The entry-base.ts Boundary

- Only react-server layer file
- All react-server-dom-webpack/* imports here
- ComponentMod provides access elsewhere
- Turbopack remaps to react-server-dom-turbopack silently

## Common Mistakes

| Error | File | Root Cause |
|---|---|---|
| Hook in server component | `react-client-hook-in-server-component.mdx` | Missing "use client" |
| Context in server component | `context-in-server-component.mdx` | Provider needs client wrapper |
| Class in server component | `class-component-in-server-component.mdx` | Classes not supported in SC |
| Async client component | `no-async-client-component.mdx` | async only for server components |
| Invalid server value | `invalid-use-server-value.mdx` | Non-serializable return from action |

## Patterns for Fixing Boundary Errors

- **Client wrapper**: Extract interactive parts to a "use client" component
- **Server data + client interactivity**: Pass serializable data as props
- **Composition pattern**: Server component renders client component children
