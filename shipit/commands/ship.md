---
description: Full ship cycle. Reviews staged files, runs pre-commit checks, commits, pushes, and verifies the build started. Stops on any failure.
allowed-tools: Bash, Read, Glob
argument-hint: [optional commit message]
---

1. Run `git status`. If working tree is dirty with unstaged changes,
   show them and ask what to include.
2. Run `git diff --staged --stat`. Flag unexpected files.
3. Run pre-commit checks per the project type table in CLAUDE.md.
   If any check fails, show the error and STOP.
4. Confirm the commit message (suggest one if not provided).
5. Commit.
6. Push to the current branch.
7. If push fails (rejected, auth error), show the error and suggest
   a fix (pull --rebase, force push if appropriate, etc.).
8. After push, check for CI/CD:
   - If Vercel: note that deploy is triggered automatically.
     Run `vercel ls` if the CLI is available.
   - If Railway: note that deploy is triggered automatically.
     Run `railway status` if the CLI is available.
   - If neither CLI is available, say so and suggest checking
     the dashboard manually.
9. Show final summary: commit hash, branch, push status, deploy status.
