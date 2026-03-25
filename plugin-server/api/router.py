"""Django Ninja API router with all endpoints."""

import threading

from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Query
from ninja.errors import HttpError
from ninja.throttling import AnonRateThrottle

from plugins.models import (
    AgentDefinition,
    IngestionRun,
    Plugin,
    ReferenceDoc,
    SourceChunk,
    Template,
)

from .schemas import (
    AgentDetail,
    AgentSummary,
    ErrorResponse,
    PluginContext,
    PluginDetail,
    PluginSummary,
    ReferenceDetail,
    ReferenceSummary,
    SearchRequest,
    SearchResult,
    SourceChunkSchema,
    SourceFileDetail,
    SourceFileSummary,
    SourceSearchRequest,
    SyncResponse,
    TemplateDetail,
    TemplateSummary,
)

api = NinjaAPI(
    title="Codex Plugin Server",
    version="1.0.0",
    description="Universal MCP access point for the Codex plugin ecosystem",
    throttle=[AnonRateThrottle("60/m")],
)


# ==================== Plugins ====================


@api.get("/plugins/", response=list[PluginSummary], tags=["plugins"])
def list_plugins(request):
    """List all plugins with descriptions."""
    return list(
        Plugin.objects.values("slug", "name", "version", "description")
    )


@api.get("/plugins/{slug}/", response=PluginDetail, tags=["plugins"])
def get_plugin(request, slug: str):
    """Plugin detail with content counts."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    return PluginDetail(
        slug=plugin.slug,
        name=plugin.name,
        version=plugin.version,
        description=plugin.description,
        claude_md=plugin.claude_md,
        agents_md=plugin.agents_md,
        manifest=plugin.manifest,
        agent_count=plugin.agents.filter(is_deleted=False).count(),
        reference_count=plugin.references.filter(is_deleted=False).count(),
        source_chunk_count=plugin.source_chunks.filter(is_deleted=False).count(),
        template_count=plugin.templates.filter(is_deleted=False).count(),
    )


@api.get("/plugins/{slug}/context", response=PluginContext, tags=["plugins"])
def get_plugin_context(request, slug: str):
    """CLAUDE.md + agents routing table. Call first when using a plugin."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    agents = plugin.agents.filter(is_deleted=False).values("slug", "name")
    return PluginContext(
        slug=plugin.slug,
        name=plugin.name,
        claude_md=plugin.claude_md,
        agents_md=plugin.agents_md,
        agents=[
            AgentSummary(slug=a["slug"], name=a["name"], plugin_slug=plugin.slug)
            for a in agents
        ],
    )


# ==================== Agents ====================


@api.get("/plugins/{slug}/agents/", response=list[AgentSummary], tags=["agents"])
def list_agents(request, slug: str):
    """List agents for a plugin."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    return [
        AgentSummary(slug=a.slug, name=a.name, plugin_slug=plugin.slug)
        for a in plugin.agents.filter(is_deleted=False)
    ]


@api.get(
    "/plugins/{slug}/agents/{agent_slug}/",
    response=AgentDetail,
    tags=["agents"],
)
def get_agent(request, slug: str, agent_slug: str):
    """Load a single agent definition."""
    agent = get_object_or_404(
        AgentDefinition,
        plugin__slug=slug,
        slug=agent_slug,
        is_deleted=False,
    )
    return AgentDetail(
        slug=agent.slug,
        name=agent.name,
        plugin_slug=slug,
        content=agent.content,
    )


# ==================== References ====================


@api.get(
    "/plugins/{slug}/references/",
    response=list[ReferenceSummary],
    tags=["references"],
)
def list_references(request, slug: str, doc_type: str | None = Query(None)):
    """List reference docs for a plugin, optionally filtered by type."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    qs = plugin.references.filter(is_deleted=False)
    if doc_type:
        qs = qs.filter(doc_type=doc_type)
    return [
        ReferenceSummary(
            slug=r.slug, title=r.title, doc_type=r.doc_type, file_path=r.file_path
        )
        for r in qs
    ]


@api.get(
    "/plugins/{slug}/references/{ref_slug}/",
    response=ReferenceDetail,
    tags=["references"],
)
def get_reference(request, slug: str, ref_slug: str):
    """Load a single reference doc."""
    ref = get_object_or_404(
        ReferenceDoc,
        plugin__slug=slug,
        slug=ref_slug,
        is_deleted=False,
    )
    return ReferenceDetail(
        slug=ref.slug,
        title=ref.title,
        doc_type=ref.doc_type,
        file_path=ref.file_path,
        plugin_slug=slug,
        content=ref.content,
    )


# ==================== Source ====================


@api.get(
    "/plugins/{slug}/source/{ref_library}/",
    response=list[SourceFileSummary],
    tags=["source"],
)
def list_source_files(request, slug: str, ref_library: str):
    """List files in a ref library."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    files = (
        plugin.source_chunks.filter(
            ref_library=ref_library, is_deleted=False
        )
        .values("file_path", "language")
        .annotate(chunk_count=Count("id"))
        .order_by("file_path")
    )
    return [
        SourceFileSummary(
            file_path=f["file_path"],
            language=f["language"],
            chunk_count=f["chunk_count"],
        )
        for f in files
    ]


@api.get(
    "/plugins/{slug}/source/{ref_library}/{path:path}",
    response=SourceFileDetail,
    tags=["source"],
)
def get_source_file(request, slug: str, ref_library: str, path: str):
    """Reassemble a source file from its chunks."""
    full_path = f"refs/{ref_library}/{path}"
    chunks = SourceChunk.objects.filter(
        plugin__slug=slug,
        ref_library=ref_library,
        file_path=full_path,
        is_deleted=False,
    ).order_by("start_line")

    if not chunks.exists():
        raise HttpError(404, "Source file not found")

    first = chunks.first()
    content = "\n".join(c.content for c in chunks)
    return SourceFileDetail(
        file_path=full_path,
        ref_library=ref_library,
        language=first.language,
        plugin_slug=slug,
        content=content,
    )


# ==================== Templates ====================


@api.get(
    "/plugins/{slug}/templates/",
    response=list[TemplateSummary],
    tags=["templates"],
)
def list_templates(request, slug: str):
    """List templates for a plugin."""
    plugin = get_object_or_404(Plugin, slug=slug, is_deleted=False)
    return [
        TemplateSummary(
            slug=t.slug,
            name=t.name,
            category=t.category,
            language=t.language,
            file_path=t.file_path,
        )
        for t in plugin.templates.filter(is_deleted=False)
    ]


@api.get(
    "/plugins/{slug}/templates/{category}/{name}/",
    response=TemplateDetail,
    tags=["templates"],
)
def get_template(request, slug: str, category: str, name: str):
    """Load a single template."""
    template = get_object_or_404(
        Template,
        plugin__slug=slug,
        category=category,
        slug=name,
        is_deleted=False,
    )
    return TemplateDetail(
        slug=template.slug,
        name=template.name,
        category=template.category,
        language=template.language,
        file_path=template.file_path,
        plugin_slug=slug,
        content=template.content,
    )


# ==================== Search ====================


def _fulltext_search(qs, fields, query_text, limit):
    """Apply PostgreSQL full-text search across given fields."""
    sv = SearchVector(*fields)
    sq = SearchQuery(query_text)
    return (
        qs.annotate(rank=SearchRank(sv, sq))
        .filter(rank__gte=0.01)
        .order_by("-rank")[:limit]
    )


@api.post("/search/", response=list[SearchResult], tags=["search"])
def search_all(request, body: SearchRequest):
    """Search across all content types."""
    results = []

    if body.content_type in (None, "agent"):
        qs = AgentDefinition.objects.filter(is_deleted=False)
        if body.plugin:
            qs = qs.filter(plugin__slug=body.plugin)
        for a in _fulltext_search(qs, ["content", "name"], body.query, body.limit):
            results.append(SearchResult(
                content_type="agent",
                plugin_slug=a.plugin.slug,
                title=a.name,
                slug=a.slug,
                snippet=a.content[:300],
                rank=a.rank,
            ))

    if body.content_type in (None, "reference"):
        qs = ReferenceDoc.objects.filter(is_deleted=False)
        if body.plugin:
            qs = qs.filter(plugin__slug=body.plugin)
        for r in _fulltext_search(qs, ["content", "title"], body.query, body.limit):
            results.append(SearchResult(
                content_type="reference",
                plugin_slug=r.plugin.slug,
                title=r.title,
                slug=r.slug,
                snippet=r.content[:300],
                rank=r.rank,
            ))

    if body.content_type in (None, "source"):
        qs = SourceChunk.objects.filter(is_deleted=False)
        if body.plugin:
            qs = qs.filter(plugin__slug=body.plugin)
        for s in _fulltext_search(
            qs, ["content", "symbol_name"], body.query, body.limit
        ):
            results.append(SearchResult(
                content_type="source",
                plugin_slug=s.plugin.slug,
                title=f"{s.ref_library}::{s.symbol_name or s.file_path}",
                slug=s.file_path,
                snippet=s.content[:300],
                rank=s.rank,
            ))

    results.sort(key=lambda r: r.rank, reverse=True)
    return results[: body.limit]


@api.post("/search/source/", response=list[SearchResult], tags=["search"])
def search_source(request, body: SourceSearchRequest):
    """Search source chunks only."""
    qs = SourceChunk.objects.filter(is_deleted=False)
    if body.plugin:
        qs = qs.filter(plugin__slug=body.plugin)
    if body.ref_library:
        qs = qs.filter(ref_library=body.ref_library)
    if body.language:
        qs = qs.filter(language=body.language)

    results = []
    for s in _fulltext_search(qs, ["content", "symbol_name"], body.query, body.limit):
        results.append(SearchResult(
            content_type="source",
            plugin_slug=s.plugin.slug,
            title=f"{s.ref_library}::{s.symbol_name or s.file_path}",
            slug=s.file_path,
            snippet=s.content[:300],
            rank=s.rank,
        ))
    return results


@api.post("/search/agents/", response=list[SearchResult], tags=["search"])
def search_agents(request, body: SearchRequest):
    """Search agent definitions only."""
    qs = AgentDefinition.objects.filter(is_deleted=False)
    if body.plugin:
        qs = qs.filter(plugin__slug=body.plugin)

    results = []
    for a in _fulltext_search(qs, ["content", "name"], body.query, body.limit):
        results.append(SearchResult(
            content_type="agent",
            plugin_slug=a.plugin.slug,
            title=a.name,
            slug=a.slug,
            snippet=a.content[:300],
            rank=a.rank,
        ))
    return results


# ==================== Admin ====================


@api.post(
    "/admin/sync/",
    response={200: SyncResponse, 403: ErrorResponse},
    tags=["admin"],
)
def trigger_sync(request):
    """Trigger a GitHub re-sync. Requires PLUGIN_SERVER_ADMIN_KEY."""
    admin_key = settings.PLUGIN_SERVER_ADMIN_KEY
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

    if not admin_key or token != admin_key:
        return 403, ErrorResponse(detail="Invalid or missing admin key")

    from django.core.management import call_command

    def run_sync():
        call_command("sync_plugins")

    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()

    return 200, SyncResponse(
        status="started",
        message="Sync started in background",
    )
