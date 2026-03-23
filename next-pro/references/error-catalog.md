# Error Catalog

> Structured index of all error MDX files by category and symptom.
> The triage agent's primary lookup table.
>
> **Build instruction**: Generate from `errors/*.mdx` -- read filenames
> and first ~5 lines of each file, then categorize.

## By Category

### Hydration & Rendering
| File | Title | Key Symptom |
|---|---|---|
| `react-hydration-error.mdx` | React Hydration Error | Text content / DOM structure mismatch |
| `deopted-into-client-rendering.mdx` | Client Rendering Bailout | Forced client-side rendering |
| `missing-suspense-with-csr-bailout.mdx` | Missing Suspense | CSR bailout without Suspense boundary |
<!-- TODO: Complete after install.sh populates errors/ -->

### Server Components & Boundaries
| File | Title | Key Symptom |
|---|---|---|
| `class-component-in-server-component.mdx` | Class Component in SC | Class component used in server context |
| `react-client-hook-in-server-component.mdx` | Client Hook in SC | Hook used in server component |
| `context-in-server-component.mdx` | Context in SC | createContext in server component |
| `no-async-client-component.mdx` | Async Client Component | async/await in client component |
| `invalid-use-server-value.mdx` | Invalid use server | Invalid value from server action |
| `failed-to-find-server-action.mdx` | Missing Server Action | Server action not found |
<!-- TODO: Complete after install.sh populates errors/ -->

### Routing & Navigation
| File | Title | Key Symptom |
|---|---|---|
| `slot-missing-default.mdx` | Missing Default Slot | Parallel route slot missing default |
| `blocking-route.mdx` | Blocking Route | Route blocking navigation |
| `conflicting-ssg-paths.mdx` | Conflicting Paths | SSG path conflicts |
| `app-dir-dynamic-href.mdx` | Dynamic Href | Invalid dynamic href |
| `app-static-to-dynamic-error.mdx` | Static to Dynamic | Static page forced dynamic |
| `dynamic-server-error.mdx` | Dynamic Server Usage | Dynamic API in static context |
<!-- TODO: Complete after install.sh populates errors/ -->

### Build & Configuration
| File | Title | Key Symptom |
|---|---|---|
| `invalid-next-config.mdx` | Invalid Config | Config validation failure |
| `module-not-found.mdx` | Module Not Found | Missing module at build |
| `swc-disabled.mdx` | SWC Disabled | SWC compiler disabled |
| `failed-loading-swc.mdx` | SWC Load Failure | SWC binary not found |
<!-- TODO: Complete after install.sh populates errors/ -->

### Images
| File | Title | Key Symptom |
|---|---|---|
| `next-image-unconfigured-host.mdx` | Unconfigured Host | Image host not in config |
| `next-image-missing-loader.mdx` | Missing Loader | Custom loader not configured |
| `install-sharp.mdx` | Sharp Missing | Sharp package not installed |
<!-- TODO: Complete after install.sh populates errors/ -->

### CSS & Styling
| File | Title | Key Symptom |
|---|---|---|
| `css-global.mdx` | Global CSS | Global CSS import issue |
| `css-modules-npm.mdx` | CSS Modules NPM | CSS modules from node_modules |
<!-- TODO: Complete after install.sh populates errors/ -->

### API Routes & Server Actions
| File | Title | Key Symptom |
|---|---|---|
| `api-routes-response-size-limit.mdx` | Response Size | API response too large |
| `api-routes-static-export.mdx` | Static Export | API routes with static export |
<!-- TODO: Complete after install.sh populates errors/ -->

### Edge & Middleware
| File | Title | Key Symptom |
|---|---|---|
| `edge-dynamic-code-evaluation.mdx` | Dynamic Code in Edge | Dynamic code in edge runtime |
| `node-module-in-edge-runtime.mdx` | Node Module in Edge | Node.js API in edge |
| `middleware-upgrade-guide.mdx` | Middleware Upgrade | Middleware API changes |
<!-- TODO: Complete after install.sh populates errors/ -->

### Static Generation & ISR
| File | Title | Key Symptom |
|---|---|---|
| `prerender-error.mdx` | Prerender Error | Static generation failure |
| `static-page-generation-timeout.mdx` | Generation Timeout | Static page timeout |
<!-- TODO: Complete after install.sh populates errors/ -->

### Legacy (Pages Router)
<!-- TODO: Complete after install.sh populates errors/ -->

## By Error Text Fragment

| Fragment | File |
|---|---|
| "Text content does not match" | `react-hydration-error.mdx` |
| "Hydration failed because" | `react-hydration-error.mdx` |
| "deopted into client-side rendering" | `deopted-into-client-rendering.mdx` |
| "Module not found" | `module-not-found.mdx` |
| "You're importing a component that needs" | `react-client-hook-in-server-component.mdx` |
| "createContext is not supported" | `context-in-server-component.mdx` |
| "async/await is not yet supported in Client Components" | `no-async-client-component.mdx` |
| "Static generation failed" | `prerender-error.mdx` |
| "Dynamic server usage" | `dynamic-server-error.mdx` |
| "Failed to find Server Action" | `failed-to-find-server-action.mdx` |
| "Invariant: missing default export" | `slot-missing-default.mdx` |
| "Invalid next.config" | `invalid-next-config.mdx` |

## By Next.js Error URL

| URL Slug | File | Category |
|---|---|---|
| `react-hydration-error` | `react-hydration-error.mdx` | Hydration |
| `deopted-into-client-rendering` | `deopted-into-client-rendering.mdx` | Hydration |
| `module-not-found` | `module-not-found.mdx` | Build |
| `react-client-hook-in-server-component` | `react-client-hook-in-server-component.mdx` | RSC |
<!-- TODO: Complete after install.sh populates errors/ -->
