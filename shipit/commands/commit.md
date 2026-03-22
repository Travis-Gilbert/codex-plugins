---
description: Review staged changes, flag unexpected files, and commit with a conventional commit message. Always shows the diff before committing.
allowed-tools: Bash, Read
argument-hint: [optional commit message]
---

1. Run `git status` and `git diff --staged --stat`.
2. If nothing is staged, show status and ask what to stage.
3. If unexpected files are staged (binary files, env files,
   build artifacts, files unrelated to the described work),
   flag them and ask whether to unstage.
4. Show a summary: files changed, insertions, deletions.
5. If the user provided a commit message, use it.
   Otherwise, suggest a conventional commit message based on the diff.
6. Confirm with the user, then commit.
7. Show `git log --oneline -1` to confirm.
