---
description: "Pydantic v2 with Django: schema design, model-to-schema mapping, PydanticAI agents, Django Ninja integration"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: "<Pydantic schema or integration question>"
---

# Pydantic + Django Integration

Load the pydantic-specialist agent from `${CLAUDE_PLUGIN_ROOT}/agents/pydantic-specialist.md` and follow its instructions.

Before working with Pydantic in Django:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/pydantic-django-mapping.md` for the three-layer mapping guide
2. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/pydantic/pydantic/` for Pydantic v2 internals
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-ninja/ninja/orm/` for ModelSchema bridge
4. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/pydantic-ai/` for PydanticAI patterns

Remember: Pydantic schemas define contracts, Django models define storage, DRF serializers define API representation. Do not collapse layers unless genuinely warranted.
