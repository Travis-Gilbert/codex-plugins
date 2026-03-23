# Rendering Pipeline

> The complete request lifecycle from incoming HTTP request to streamed
> HTML response and client hydration. This is the "map" that every
> other reference points into.
>
> **Source files**: start-server.ts, router-server.ts, base-server.ts,
> next-server.ts, route-module.ts, app-render.tsx, create-component-tree.tsx,
> walk-tree-with-flight-router-state.tsx, node-web-streams-helper.ts,
> app-index.tsx, app-bootstrap.ts, app-router.tsx

## 1. Server Startup

`start-server.ts` creates workers and `router-server.ts` initializes
the request handling pipeline.

<!-- TODO: Populate from refs/next-server/lib/start-server.ts -->

## 2. Request Reception

`router-server.ts` receives the incoming HTTP request and determines
the route type (page, API, static asset).

<!-- TODO: Populate from refs/next-server/lib/router-server.ts -->

## 3. Route Matching

`base-server.ts` matches the URL to a registered route and dispatches
to the appropriate route module.

<!-- TODO: Populate from refs/next-server/base-server.ts -->

## 4. App Page Rendering

`app-render.tsx` renders the component tree for App Router pages.

### 4a. Component Tree Resolution

`create-component-tree.tsx` resolves which components are server
components vs. client components and builds the render tree.

<!-- TODO: Populate from refs/next-server/app-render/create-component-tree.tsx -->

### 4b. Flight Router State

`walk-tree-with-flight-router-state.tsx` walks the layout and page
tree to produce the Flight router state.

<!-- TODO: Populate from refs/next-server/app-render/walk-tree-with-flight-router-state.tsx -->

### 4c. Streaming

The response streams to the client via `node-web-streams-helper.ts`.

<!-- TODO: Populate from refs/next-server/stream-utils/node-web-streams-helper.ts -->

## 5. Client Hydration

### 5a. Bootstrap

`app-bootstrap.ts` initializes the client-side JavaScript.

<!-- TODO: Populate from refs/next-client/app-bootstrap.ts -->

### 5b. Router Mount

`app-router.tsx` takes over navigation after hydration completes.

<!-- TODO: Populate from refs/next-client/components/app-router.tsx -->

## 6. Subsequent Navigations

Client-side navigation via the router reducer and `fetch-server-response.ts`.

<!-- TODO: Populate from refs/next-client/components/router-reducer/ -->
