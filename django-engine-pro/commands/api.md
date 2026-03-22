---
description: "Design Django APIs with DRF or Django Ninja: framework selection, serializers, viewsets, schemas, filtering, pagination"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, Agent
argument-hint: "<API endpoint or design question>"
---

# Django API Design

Load the api-architect agent from `${CLAUDE_PLUGIN_ROOT}/agents/api-architect.md` and follow its instructions.

Before designing any API:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/api-decision-framework.md` for the DRF vs Ninja comparison
2. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-rest-framework/rest_framework/serializers.py` for DRF patterns
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-ninja/ninja/` for Ninja patterns
4. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-filter/` for FilterSet patterns

If the API involves polymorphic models, also load the polymorphic-engineer agent. If it involves Pydantic schemas, also load the pydantic-specialist agent.
