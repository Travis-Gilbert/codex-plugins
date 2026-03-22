---
description: "Optimize Django ORM queries: N+1 detection, select_related/prefetch_related, aggregations, window functions, raw SQL"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: "<query or performance problem description>"
---

# Django ORM Optimization

Load the orm-specialist agent from `${CLAUDE_PLUGIN_ROOT}/agents/orm-specialist.md` and follow its instructions.

Before optimizing any query:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/orm-performance.md` for the performance playbook
2. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-db/models/query.py` for QuerySet internals
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-db/models/expressions.py` for F, Case/When, Window

Run through the anti-pattern detection checklist on any existing code before suggesting improvements. Flag N+1 loops, missing prefetch, count-via-len, and exists-via-bool.
