# ShipIt

Git and deployment automation for Claude Code. Verification at every step.

## Commands

| Command | Description |
|---------|-------------|
| `/commit` | Review staged changes, flag unexpected files, commit with conventional message |
| `/ship` | Full cycle: stage review → pre-commit checks → commit → push → build verify |
| `/deploy-check` | Verify a deployment is live and responding |

## Installation

### Via sync-plugins.sh

From the `codex-plugins/` directory:

```bash
./sync-plugins.sh
```

### Manual

```bash
claude --plugin-dir /path/to/codex-plugins/shipit
```

## How It Works

### /commit

Shows `git diff --staged --stat`, flags unexpected files (binaries, .env, build artifacts), suggests a conventional commit message, and confirms before committing.

### /ship

Everything `/commit` does, plus:
- Runs pre-commit checks based on project type (TypeScript type-check, Django check, lint/format)
- Pushes to the current branch
- Detects CI/CD target (Vercel, Railway) and reports deploy status

### /deploy-check

Verifies a deployment by URL or project name:
- HTTP status and response time
- Framework-specific smoke tests (Django admin, Next.js HTML check)
- Suggests debugging steps if unhealthy

## Deploy Target Detection

| Signal | Target |
|--------|--------|
| `vercel.json` or `.vercel/` | Vercel |
| `next.config.*` (no Railway) | Vercel (Next.js) |
| `railway.toml` or `Procfile` + Django | Railway |
| `requirements.txt` + `manage.py` | Railway (Django) |

## Pre-commit Checks

| Project Type | Checks Run |
|-------------|------------|
| Next.js / React (TypeScript) | `npx tsc --noEmit`, `npm run build` |
| Django | `python manage.py check`, `python manage.py test --parallel` |
| General | Lint/format from `package.json` or `Makefile` |

## License

MIT
