# Hydration Patterns

> Every known hydration mismatch pattern with source-backed explanation
> and fix. The hydration agent's primary lookup.
>
> **Source files**: react-hydration-error.mdx, deopted-into-client-rendering.mdx,
> app-render.tsx, dynamic-rendering.ts, create-error-handler.tsx,
> app-index.tsx, error-boundary.tsx, dynamic.tsx

## How Hydration Works in Next.js

Server renders HTML via `app-render.tsx`, client calls `hydrateRoot`
via `app-index.tsx`, React diffs the DOM against the virtual tree.
Any mismatch triggers a hydration error.

<!-- TODO: Populate with specifics from source -->

## Pattern Catalog

### 1. Browser-Only Values
- **Symptom**: Text content mismatch
- **Source**: Render path reads `window`, `Date`, `Math.random`
- **Fix**: `useEffect` pattern, `suppressHydrationWarning`, `next/dynamic` with `ssr: false`

### 2. Invalid HTML Nesting
- **Symptom**: DOM structure mismatch
- **Source**: Browser auto-corrects invalid nesting before React hydrates
- **Fix**: Use semantic elements, validate nesting

### 3. Browser Extension Interference
- **Symptom**: Unexpected DOM modifications
- **Source**: Extensions (Grammarly, LastPass) modify DOM before hydration
- **Fix**: Document as known cause; `suppressHydrationWarning` on specific elements

### 4. CSS-in-JS Misconfiguration
- **Symptom**: Style mismatches, FOUC
- **Source**: Style injection not configured for SSR
- **Fix**: Follow library-specific SSR configuration

### 5. iOS Auto-Detection
- **Symptom**: iOS-only hydration warnings
- **Source**: Safari auto-links phone numbers, emails, dates
- **Fix**: `<meta name="format-detection" content="telephone=no, date=no, email=no, address=no" />`

### 6. Streaming/Suspense Boundary Mismatches
- **Symptom**: Content appears then disappears or shifts
- **Source**: Suspense boundary resolution timing
- **Fix**: Verify Suspense boundary placement

### 7. Dynamic Rendering Bailout
- **Symptom**: Static HTML doesn't match dynamic client render
- **Source**: `dynamic-rendering.ts` bailout conditions
- **Fix**: Add proper Suspense boundaries or accept dynamic rendering

### 8. Edge Cases
- Format-detection meta tags
- Third-party scripts modifying DOM
- Concurrent mode timing
