# MCP Toolset Template

Django app exposing models via django-mcp-server with scoped querysets,
authentication, and both ModelQueryToolset and custom MCPToolset patterns.

## Files

- `mcp.py` — ModelQueryToolset and custom MCPToolset definitions
- `settings_fragment.py` — Required settings additions
- `urls_fragment.py` — URL routing for MCP endpoint

## Safety Checklist

- [ ] Every ModelQueryToolset has scoped get_queryset()
- [ ] Authentication is configured in settings
- [ ] Async tools use async ORM exclusively
- [ ] Every tool has a descriptive docstring
- [ ] Tool return values are serializable (no lazy QuerySets)
