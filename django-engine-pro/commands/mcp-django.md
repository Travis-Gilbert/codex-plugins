---
description: "Build MCP servers from Django: ModelQueryToolset, custom toolsets, DRF bridge, queryset scoping, async ORM"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion, Agent
argument-hint: "<MCP server design or question>"
---

# Django MCP Server Construction

Load the mcp-builder agent from `${CLAUDE_PLUGIN_ROOT}/agents/mcp-builder.md` and follow its instructions.

Before building any MCP server:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/mcp-patterns.md` for the construction guide
2. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-mcp-server/mcp_server/` for source-level details
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/pydantic-ai/pydantic_ai_slim/pydantic_ai/mcp.py` for the client side

Enforce safety rules: every ModelQueryToolset MUST have scoped get_queryset(), authentication MUST be configured, and async tools MUST use async ORM exclusively.
