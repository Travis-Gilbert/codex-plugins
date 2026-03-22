---
description: "Design Django models with proper inheritance strategy, field selection, managers, indexes, and migration planning"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, Agent
argument-hint: "<model or domain description>"
---

# Django Model Design

Load the model-architect agent from `${CLAUDE_PLUGIN_ROOT}/agents/model-architect.md` and follow its instructions.

Before writing any model code:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/inheritance-strategies.md` if the task involves model inheritance
2. **Read** `${CLAUDE_PLUGIN_ROOT}/references/manager-queryset-patterns.md` if custom managers are needed
3. **Read** `${CLAUDE_PLUGIN_ROOT}/references/migration-strategy.md` if migration planning is involved
4. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-db/models/` to verify field types and Meta options
5. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-model-utils/` for TimeStampedModel, StatusField patterns

State the inheritance strategy and its trade-offs BEFORE writing code. Present options to the user if the choice is not obvious.
