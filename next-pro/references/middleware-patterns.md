# Middleware Patterns

> Middleware implementation and edge constraints.
>
> **Source files**: middleware.ts template, entry-base.ts,
> dce-edge-rules.md

## Execution Model

Middleware runs before every matched request in the Edge Runtime.
It can rewrite, redirect, set headers, or return a response.

## Edge Runtime Constraints

**Allowed**: fetch, Request, Response, Headers, URL, TextEncoder,
crypto.subtle, Web Streams

**Not allowed**: Node.js APIs (fs, path, child_process), Node.js
modules, large packages with Node internals

**Size limit**: 4MB bundle

## Matcher Configuration

```tsx
export const config = {
  matcher: [
    // Exclude static files and Next.js internals
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

## Common Patterns

- **Auth guard**: Check cookie/token, redirect to login
- **i18n routing**: Detect locale, rewrite to localized path
- **A/B testing**: Assign variant via cookie, rewrite to variant path
- **Geo-routing**: Use `request.geo`, rewrite to regional content
- **Security headers**: Add CSP, HSTS, X-Frame-Options

## Performance

Middleware adds latency to every matched request. Keep it lean:
- No heavy computation
- No external API calls that could be slow
- Use matcher to limit scope
