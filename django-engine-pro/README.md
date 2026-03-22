# Django-Engine-Pro

> Django backend mastery for Claude Code: model architecture, ORM optimization,
> API design (DRF + Ninja), django-polymorphic patterns, MCP server construction,
> scientific Python integration, and Pydantic v2 mapping.

## What This Is

A Claude Code plugin that makes Claude extraordinarily good at Django's engine room.
It provides agent definitions, curated reference documents, starter templates, and
pointers to library source code. Nothing here executes in production -- it is all
context and guidance for Claude Code.

## Relationship to Django-Pro (django-design)

Django-Pro treats frontend as equal to backend: HTMX, Alpine.js, Tailwind, D3,
template composition. Django-Engine-Pro owns the machinery underneath: models,
querysets, migrations, serializers, API contracts, MCP tools, and the
pandas/numpy/scipy bridge.

**Django-Pro builds the cockpit; Django-Engine-Pro builds the engine.**

## Agents

| Agent | Expertise |
|-------|-----------|
| model-architect | Model design, inheritance strategy, fields, managers, migrations |
| orm-specialist | Complex queries, N+1 detection, performance, raw SQL |
| api-architect | DRF vs Ninja, serializers, viewsets, schemas, OpenAPI |
| polymorphic-engineer | django-polymorphic patterns, performance, admin, DRF serialization |
| mcp-builder | Django MCP server construction, queryset scoping, async ORM |
| data-bridge | QuerySet-to-DataFrame, bulk ingest, computation pipelines |
| pydantic-specialist | Pydantic v2, three-layer mapping, PydanticAI agents |

## Commands

| Command | Description |
|---------|-------------|
| `/engine` | Hub: routes to the right specialist |
| `/model` | Model design and inheritance |
| `/orm` | ORM queries and performance |
| `/api` | API design (DRF / Ninja) |
| `/polymorphic` | django-polymorphic patterns |
| `/mcp-django` | MCP server construction |
| `/data-bridge` | Scientific Python integration |
| `/pydantic` | Pydantic v2 + Django patterns |

## Reference Library

| Document | Topic |
|----------|-------|
| inheritance-strategies.md | Abstract vs multi-table vs proxy vs polymorphic |
| orm-performance.md | N+1, prefetch, select_related, window functions |
| api-decision-framework.md | DRF vs Ninja structured comparison |
| polymorphic-playbook.md | django-polymorphic patterns and pitfalls |
| mcp-patterns.md | Building MCP servers from Django |
| scientific-bridge.md | QuerySet-to-DataFrame, bulk ingest, pipelines |
| pydantic-django-mapping.md | Three-way mapping (Model, Serializer, Schema) |
| migration-strategy.md | Data migrations, zero-downtime, squashing |
| manager-queryset-patterns.md | Custom managers, chainable QuerySets |

## Templates

| Template | Pattern |
|----------|---------|
| polymorphic-api/ | PolymorphicModel + DRF type-dispatching serializer |
| mcp-toolset/ | Django MCP server with model exposure |
| data-pipeline/ | QuerySet -> DataFrame -> computation -> bulk_create |
| pydantic-validated-api/ | Ninja API with Pydantic schemas |
| knowledge-graph-models/ | Typed node/edge models with polymorphic base |

## Source References (refs/)

The `refs/` directory is designed to hold library source code for grepping.
Populate it with:

```bash
# Django ORM internals (selective)
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/django/django.git refs/django-db-sparse
cd refs/django-db-sparse && git sparse-checkout set django/db/models django/db/backends/postgresql

# Other libraries (full clone, shallow)
git clone --depth 1 https://github.com/encode/django-rest-framework.git refs/django-rest-framework
git clone --depth 1 https://github.com/vitalik/django-ninja.git refs/django-ninja
git clone --depth 1 https://github.com/jazzband/django-polymorphic.git refs/django-polymorphic
git clone --depth 1 https://github.com/gts360/django-mcp-server.git refs/django-mcp-server
git clone --depth 1 https://github.com/jazzband/django-model-utils.git refs/django-model-utils
git clone --depth 1 https://github.com/chrisdev/django-pandas.git refs/django-pandas
git clone --depth 1 https://github.com/django-filter/django-filter.git refs/django-filter
git clone --depth 1 https://github.com/pydantic/pydantic.git refs/pydantic
git clone --depth 1 https://github.com/pydantic/pydantic-ai.git refs/pydantic-ai
git clone --depth 1 https://github.com/pydanny/dj-notebook.git refs/dj-notebook
```

## Install

The plugin is managed through the codex-plugins sync system:

```bash
cd /path/to/codex-plugins
./sync-plugins.sh
```

Then enable in `~/.claude/settings.json`:
```json
{
  "enabledPlugins": {
    "django-engine-pro@local-desktop-app-uploads": true
  }
}
```
