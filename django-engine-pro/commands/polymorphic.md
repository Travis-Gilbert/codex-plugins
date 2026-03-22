---
description: "Design and implement django-polymorphic models with performance controls, admin integration, and DRF serialization"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, Agent
argument-hint: "<polymorphic model design or question>"
---

# Django Polymorphic Models

Load the polymorphic-engineer agent from `${CLAUDE_PLUGIN_ROOT}/agents/polymorphic-engineer.md` and follow its instructions.

Before working with polymorphic models:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/polymorphic-playbook.md` for patterns and pitfalls
2. **Read** `${CLAUDE_PLUGIN_ROOT}/references/inheritance-strategies.md` to confirm polymorphic is the right choice
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-polymorphic/src/polymorphic/` for source-level details

Verify ALL four conditions for polymorphic usage:
1. Single queryset returning mixed types
2. Each type has own additional fields
3. Need actual subclass instances
4. Type count is bounded and grows slowly

If building a polymorphic API, also load the api-architect agent for serializer dispatch patterns.
