"""
MCP SSE endpoint wrapping the Ninja API as MCP tools.

Implements a lightweight SSE-based MCP server that exposes
plugin content through standardized MCP tool definitions.
"""

import json
import uuid

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from plugins.models import (
    AgentDefinition,
    Plugin,
    ReferenceDoc,
    SourceChunk,
    Template,
)
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

# ---------- MCP Tool Definitions ----------

MCP_TOOLS = [
    {
        "name": "list_plugins",
        "description": "List all available plugins with descriptions.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_plugin_context",
        "description": "Load CLAUDE.md + agent routing table for a plugin. Call first when using a plugin.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {
                    "type": "string",
                    "description": "Plugin slug (e.g., 'd3-pro')",
                },
            },
            "required": ["plugin"],
        },
    },
    {
        "name": "get_agent",
        "description": "Load a specialist agent definition.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string", "description": "Plugin slug"},
                "agent": {"type": "string", "description": "Agent slug"},
            },
            "required": ["plugin", "agent"],
        },
    },
    {
        "name": "get_reference",
        "description": "Load a curated knowledge/reference doc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string", "description": "Plugin slug"},
                "reference": {"type": "string", "description": "Reference slug"},
            },
            "required": ["plugin", "reference"],
        },
    },
    {
        "name": "get_source_file",
        "description": "Retrieve a source file from a plugin's refs/ directory for API verification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string", "description": "Plugin slug"},
                "ref_library": {"type": "string", "description": "Reference library name"},
                "file_path": {"type": "string", "description": "File path within the ref library"},
            },
            "required": ["plugin", "ref_library", "file_path"],
        },
    },
    {
        "name": "search_knowledge",
        "description": "Search across all plugin knowledge (agents, references, source).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "plugin": {"type": "string", "description": "Optional: limit to plugin slug"},
                "content_type": {
                    "type": "string",
                    "enum": ["agent", "reference", "source"],
                    "description": "Optional: limit to content type",
                },
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_source",
        "description": "Search source code references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "plugin": {"type": "string", "description": "Optional: limit to plugin slug"},
                "ref_library": {"type": "string", "description": "Optional: limit to ref library"},
                "language": {"type": "string", "description": "Optional: filter by language"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_template",
        "description": "Retrieve a starter template.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "plugin": {"type": "string", "description": "Plugin slug"},
                "category": {"type": "string", "description": "Template category"},
                "name": {"type": "string", "description": "Optional: template name/slug"},
            },
            "required": ["plugin", "category"],
        },
    },
]


# ---------- Tool Handlers ----------


def _handle_list_plugins(args):
    plugins = Plugin.objects.values("slug", "name", "version", "description")
    return [dict(p) for p in plugins]


def _handle_get_plugin_context(args):
    try:
        plugin = Plugin.objects.get(slug=args["plugin"], is_deleted=False)
    except Plugin.DoesNotExist:
        return {"error": f"Plugin '{args['plugin']}' not found"}

    agents = list(
        plugin.agents.filter(is_deleted=False).values("slug", "name")
    )
    return {
        "slug": plugin.slug,
        "name": plugin.name,
        "claude_md": plugin.claude_md,
        "agents_md": plugin.agents_md,
        "agents": agents,
    }


def _handle_get_agent(args):
    try:
        agent = AgentDefinition.objects.select_related("plugin").get(
            plugin__slug=args["plugin"], slug=args["agent"], is_deleted=False
        )
    except AgentDefinition.DoesNotExist:
        return {"error": f"Agent '{args['agent']}' not found in '{args['plugin']}'"}
    return {
        "slug": agent.slug,
        "name": agent.name,
        "plugin": agent.plugin.slug,
        "content": agent.content,
    }


def _handle_get_reference(args):
    try:
        ref = ReferenceDoc.objects.select_related("plugin").get(
            plugin__slug=args["plugin"], slug=args["reference"], is_deleted=False
        )
    except ReferenceDoc.DoesNotExist:
        return {"error": f"Reference '{args['reference']}' not found in '{args['plugin']}'"}
    return {
        "slug": ref.slug,
        "title": ref.title,
        "doc_type": ref.doc_type,
        "content": ref.content,
    }


def _handle_get_source_file(args):
    full_path = f"refs/{args['ref_library']}/{args['file_path']}"
    chunks = SourceChunk.objects.filter(
        plugin__slug=args["plugin"],
        ref_library=args["ref_library"],
        file_path=full_path,
        is_deleted=False,
    ).order_by("start_line")

    if not chunks.exists():
        return {"error": "Source file not found"}

    content = "\n".join(c.content for c in chunks)
    return {
        "file_path": full_path,
        "ref_library": args["ref_library"],
        "content": content,
    }


def _handle_search_knowledge(args):
    query_text = args["query"]
    plugin = args.get("plugin")
    content_type = args.get("content_type")
    limit = args.get("limit", 20)
    results = []

    if content_type in (None, "agent"):
        qs = AgentDefinition.objects.filter(is_deleted=False)
        if plugin:
            qs = qs.filter(plugin__slug=plugin)
        sv = SearchVector("content", "name")
        sq = SearchQuery(query_text)
        for a in qs.annotate(rank=SearchRank(sv, sq)).filter(rank__gte=0.01).order_by("-rank")[:limit]:
            results.append({
                "type": "agent",
                "plugin": a.plugin.slug if hasattr(a, "plugin") else "",
                "title": a.name,
                "slug": a.slug,
                "snippet": a.content[:300],
            })

    if content_type in (None, "reference"):
        qs = ReferenceDoc.objects.filter(is_deleted=False)
        if plugin:
            qs = qs.filter(plugin__slug=plugin)
        sv = SearchVector("content", "title")
        sq = SearchQuery(query_text)
        for r in qs.annotate(rank=SearchRank(sv, sq)).filter(rank__gte=0.01).order_by("-rank")[:limit]:
            results.append({
                "type": "reference",
                "plugin": r.plugin.slug if hasattr(r, "plugin") else "",
                "title": r.title,
                "slug": r.slug,
                "snippet": r.content[:300],
            })

    if content_type in (None, "source"):
        qs = SourceChunk.objects.filter(is_deleted=False)
        if plugin:
            qs = qs.filter(plugin__slug=plugin)
        sv = SearchVector("content", "symbol_name")
        sq = SearchQuery(query_text)
        for s in qs.annotate(rank=SearchRank(sv, sq)).filter(rank__gte=0.01).order_by("-rank")[:limit]:
            results.append({
                "type": "source",
                "plugin": s.plugin.slug if hasattr(s, "plugin") else "",
                "title": f"{s.ref_library}::{s.symbol_name or s.file_path}",
                "slug": s.file_path,
                "snippet": s.content[:300],
            })

    return results[:limit]


def _handle_search_source(args):
    query_text = args["query"]
    limit = args.get("limit", 20)
    qs = SourceChunk.objects.filter(is_deleted=False)
    if args.get("plugin"):
        qs = qs.filter(plugin__slug=args["plugin"])
    if args.get("ref_library"):
        qs = qs.filter(ref_library=args["ref_library"])
    if args.get("language"):
        qs = qs.filter(language=args["language"])

    sv = SearchVector("content", "symbol_name")
    sq = SearchQuery(query_text)
    results = []
    for s in qs.annotate(rank=SearchRank(sv, sq)).filter(rank__gte=0.01).order_by("-rank")[:limit]:
        results.append({
            "type": "source",
            "plugin": s.plugin.slug if hasattr(s, "plugin") else "",
            "title": f"{s.ref_library}::{s.symbol_name or s.file_path}",
            "file_path": s.file_path,
            "snippet": s.content[:300],
        })
    return results


def _handle_get_template(args):
    qs = Template.objects.filter(
        plugin__slug=args["plugin"],
        category=args["category"],
        is_deleted=False,
    )
    if args.get("name"):
        qs = qs.filter(slug=args["name"])

    templates = list(qs.values("slug", "name", "category", "language", "content"))
    if not templates:
        return {"error": "Template not found"}
    if len(templates) == 1:
        return templates[0]
    return templates


TOOL_HANDLERS = {
    "list_plugins": _handle_list_plugins,
    "get_plugin_context": _handle_get_plugin_context,
    "get_agent": _handle_get_agent,
    "get_reference": _handle_get_reference,
    "get_source_file": _handle_get_source_file,
    "search_knowledge": _handle_search_knowledge,
    "search_source": _handle_search_source,
    "get_template": _handle_get_template,
}


# ---------- SSE Transport ----------

# In-memory session store (production would use Redis)
_sessions: dict[str, dict] = {}


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@require_GET
def mcp_sse(request):
    """SSE endpoint. Opens a session and streams the endpoint URL."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"initialized": False}

    def event_stream():
        # Send the endpoint URL for the client to POST messages to
        yield _sse_event(
            "endpoint",
            f"/mcp/messages/?session_id={session_id}",
        )
        # Keep connection alive — client will POST to messages endpoint
        # In production, this would use async generators with proper
        # event dispatching. For Phase 1, we rely on request-response
        # via the messages endpoint.

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@csrf_exempt
@require_POST
def mcp_messages(request):
    """Handle MCP JSON-RPC messages."""
    session_id = request.GET.get("session_id", "")
    if session_id not in _sessions:
        return JsonResponse(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Invalid session"}},
            status=400,
        )

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
            status=400,
        )

    method = body.get("method", "")
    msg_id = body.get("id")
    params = body.get("params", {})

    # Handle MCP protocol methods
    if method == "initialize":
        _sessions[session_id]["initialized"] = True
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": "codex-plugin-server",
                    "version": "1.0.0",
                },
            },
        })

    if method == "notifications/initialized":
        return JsonResponse({"jsonrpc": "2.0", "id": msg_id, "result": {}})

    if method == "tools/list":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": MCP_TOOLS},
        })

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(tool_name)

        if not handler:
            return JsonResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            })

        try:
            result = handler(tool_args)
            return JsonResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result, default=str)},
                    ],
                },
            })
        except Exception as e:
            return JsonResponse({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps({"error": str(e)})},
                    ],
                    "isError": True,
                },
            })

    return JsonResponse({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    })
