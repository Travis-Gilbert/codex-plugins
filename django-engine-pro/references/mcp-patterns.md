# Django MCP Server Construction Guide

## Overview

django-mcp-server exposes Django models and business logic as MCP tools that AI agents can discover and invoke. The server implements the Model Context Protocol, allowing Claude, PydanticAI agents, and other MCP clients to interact with your Django application.

## Setup

### 1. Install and Configure

```python
# settings.py
INSTALLED_APPS = [
    ...
    "mcp_server",
]

DJANGO_MCP_AUTHENTICATION_CLASSES = [
    "rest_framework.authentication.TokenAuthentication",
]
```

### 2. URL Routing

```python
# urls.py
from mcp_server.urls import urlpatterns as mcp_patterns

urlpatterns = [
    ...
    path("mcp/", include(mcp_patterns)),
]
```

## Tool Patterns

### ModelQueryToolset (Read-Only Model Exposure)

```python
from mcp_server import ModelQueryToolset

class SourceQueryTool(ModelQueryToolset):
    model = Source

    def get_queryset(self):
        """ALWAYS scope the queryset. Never expose all rows."""
        return super().get_queryset().filter(
            is_deleted=False,
            visibility="public"
        )
```

### MCPToolset (Custom Business Logic)

```python
from mcp_server import MCPToolset

class AnalysisTools(MCPToolset):
    def summarize_connections(self, object_slug: str) -> dict:
        """Get a summary of all connections for a knowledge object.

        Returns edge counts, strongest connections, and recent edges.
        """
        # Business logic here
        ...
```

### DRF Bridge (Existing Views as MCP Tools)

```python
from mcp_server import drf_publish_list_mcp_tool

@drf_publish_list_mcp_tool(instructions="Search research sources")
class SourceListView(ListAPIView):
    """List research sources with filtering."""
    serializer_class = SourceSerializer
    queryset = Source.objects.filter(is_deleted=False)
```

## Safety Rules

1. **Always scope querysets**: Override get_queryset() with appropriate filtering
2. **Always configure authentication**: Set DJANGO_MCP_AUTHENTICATION_CLASSES
3. **Use async ORM in async tools**: afilter, aget, acreate (never sync in async)
4. **Write descriptive docstrings**: They become tool descriptions in MCP
5. **Evaluate QuerySets**: Convert to list/dict before returning (no lazy evaluation across async)
6. **Limit result sizes**: Always paginate or cap results in tool functions

## Async ORM Pattern

```python
@mcp_server.tool()
async def search_sources(query: str, limit: int = 10) -> list[dict]:
    """Search sources by title or body content."""
    sources = await Source.objects.afilter(
        models.Q(title__icontains=query) | models.Q(body__icontains=query),
        is_deleted=False
    )[:limit]
    return [
        {"id": s.id, "title": s.title, "slug": s.slug}
        async for s in sources
    ]
```
