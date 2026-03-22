# ShipIt Plugin

Git and deployment automation with verification at every step.
No unverified claims of success. Every command proves its outcome.

## Commands

| Command | What It Does |
|---------|-------------|
| `/commit` | Review staged files, confirm intent, commit with message |
| `/ship` | Full cycle: stage review, commit, push, build verification |
| `/deploy-check` | Verify a deployment is live and responding |

## Rules

1. NEVER commit without first showing `git diff --staged --stat` and
   getting explicit confirmation. If unexpected files appear in the
   staging area, flag them before proceeding.

2. NEVER say "deployed successfully" without proof. Run the
   verification step and show the output.

3. When pushing to a branch that triggers CI/CD, wait for the
   build to start before reporting success. If the build system
   is not observable from the terminal, say so explicitly.

4. Commit messages follow conventional commits: type(scope): description.
   Suggest a message based on the diff, but let the user override.

5. If `git status` shows untracked files that look like they should
   be staged (new component files, new test files), mention them.
   If it shows files that look accidental (.env, node_modules,
   __pycache__), warn before staging.

## Deploy Targets

Detect the deploy target from project context:

| Signal | Target | Verification |
|--------|--------|-------------|
| `vercel.json` or `.vercel/` | Vercel | `vercel ls` for latest deployment status |
| `next.config.*` + no railway | Vercel (Next.js) | `npm run build` locally, then Vercel auto-deploys on push |
| `railway.toml` or `Procfile` + Django | Railway | `railway status` or curl the health endpoint |
| `requirements.txt` + `manage.py` | Railway (Django) | `python manage.py check --deploy` locally, Railway deploys on push |

If the target is ambiguous, ask. Do not guess.

## Pre-commit Checks

Before every commit, run the project's own checks:

| Project Type | Check |
|-------------|-------|
| Next.js / React | `npx tsc --noEmit` (if TypeScript), `npm run build` |
| Django | `python manage.py check`, `python manage.py test --parallel` (if tests exist) |
| General | Run whatever lint/format commands exist in package.json or Makefile |

If any check fails, show the error and stop. Do not commit broken code.
