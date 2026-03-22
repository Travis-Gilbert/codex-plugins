# Django-Engine-Pro Agent Registry

> Agent routing rules for the Django-Engine-Pro plugin. Claude Code reads this
> to determine which specialist to load for a given task.

## Agent Selection

Agents are composable context, not exclusive. A single task may load multiple
agents. Read the relevant agent .md file(s) before starting work.

### By Task Type

| Task | Primary Agent | Also Load | Key Refs |
|------|--------------|-----------|----------|
| New model design | `model-architect` | `orm-specialist` | `refs/django-db/models/`, `refs/django-model-utils/` |
| Inheritance decision | `model-architect` | `polymorphic-engineer` | `refs/django-polymorphic/`, `references/inheritance-strategies.md` |
| Complex ORM query | `orm-specialist` | -- | `refs/django-db/models/sql/` |
| Query performance | `orm-specialist` | -- | `references/orm-performance.md` |
| DRF API endpoint | `api-architect` | `orm-specialist` | `refs/django-rest-framework/` |
| Django Ninja API | `api-architect` | `pydantic-specialist` | `refs/django-ninja/ninja/` |
| API filtering | `api-architect` | -- | `refs/django-filter/` |
| Polymorphic model | `polymorphic-engineer` | `model-architect` | `refs/django-polymorphic/src/polymorphic/` |
| Polymorphic API | `polymorphic-engineer` | `api-architect` | Both framework refs + `references/polymorphic-playbook.md` |
| MCP server setup | `mcp-builder` | `api-architect` | `refs/django-mcp-server/mcp_server/` |
| MCP + DRF bridge | `mcp-builder` | `api-architect` | Both refs |
| QuerySet to DataFrame | `data-bridge` | `orm-specialist` | `refs/django-pandas/`, `references/scientific-bridge.md` |
| Bulk ingest from pandas | `data-bridge` | `model-architect` | `refs/django-pandas/`, `refs/django-db/models/` |
| Computation pipeline | `data-bridge` | -- | `references/scientific-bridge.md` |
| Pydantic schema design | `pydantic-specialist` | -- | `refs/pydantic/pydantic/` |
| PydanticAI agent | `pydantic-specialist` | `mcp-builder` | `refs/pydantic-ai/` |
| Model-to-schema mapping | `pydantic-specialist` | `api-architect` | `references/pydantic-django-mapping.md` |
| Migration planning | `model-architect` | -- | `references/migration-strategy.md` |
| Custom manager/queryset | `orm-specialist` | `model-architect` | `refs/django-db/models/manager.py`, `refs/django-model-utils/` |
| Django Jupyter exploration | `data-bridge` | -- | `refs/dj-notebook/` |

### Composition Rules

- When designing a polymorphic API, load BOTH polymorphic-engineer AND
  api-architect. The serializer patterns for polymorphic models differ
  significantly from standard DRF.
- When building an MCP server that exposes model queries, load BOTH
  mcp-builder AND orm-specialist. The queryset scoping and async ORM
  patterns are critical for safety and correctness.
- When building a data pipeline that moves data between Django and
  scientific Python, load BOTH data-bridge AND orm-specialist. The
  QuerySet-to-DataFrame conversion has performance traps that the
  orm-specialist knows how to avoid.
