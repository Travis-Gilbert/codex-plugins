# Test Patterns

> How to write and run tests against Next.js applications, using
> the framework's own test infrastructure as a model.
>
> **Source files**: AGENTS.md (Next.js repo), router-act skill,
> test/lib/, test/e2e/, test/development/, test/production/

## Test Infrastructure

- `nextTestSetup` — standard test setup utility
- Test modes: dev-turbo, dev-webpack, start-turbo, start-webpack
- Fixture directories for test apps

## Running Tests

```bash
# Dev mode with Turbopack (default)
pnpm test-dev test/e2e/app-dir/app/index.test.ts

# Dev mode with webpack
pnpm test-dev-webpack test/e2e/app-dir/app/index.test.ts

# Production mode with Turbopack
pnpm test-start test/e2e/app-dir/app/index.test.ts

# Production mode with webpack
pnpm test-start-webpack test/e2e/app-dir/app/index.test.ts
```

**NEXT_SKIP_ISOLATE**: Skips the pack step for faster iteration.
Do NOT use when testing module resolution or package.json exports.

## Writing Tests

- Use `pnpm new-test` to scaffold
- Use `retry()` not `setTimeout` for async assertions
- Use fixture directories, not inline file creation
- Each test should be independent and idempotent

## Router Act Testing

From the router-act skill:
- `createRouterAct` — test utility for router actions
- `LinkAccordion` pattern — test navigation state changes

## Common Test Debugging

- Capture output to file for analysis without re-running
- Mode-specific behavior differences (dev vs. production)
- Known flaky test handling: check CI history

## Minimal Reproduction Pattern

When debugging user issues, create a minimal Next.js app:

```bash
npx create-next-app@latest repro --ts --app --tailwind --no-src-dir
cd repro
# Add minimal code to reproduce the issue
npm run dev  # or npm run build
```

Use `templates/minimal-repro.md` for the structured format.
