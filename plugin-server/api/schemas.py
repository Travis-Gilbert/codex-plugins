"""Pydantic schemas for the Django Ninja API."""

from ninja import Schema


# ---------- Plugin ----------

class PluginSummary(Schema):
    slug: str
    name: str
    version: str
    description: str


class PluginDetail(Schema):
    slug: str
    name: str
    version: str
    description: str
    claude_md: str
    agents_md: str
    manifest: dict
    agent_count: int = 0
    reference_count: int = 0
    source_chunk_count: int = 0
    template_count: int = 0


class PluginContext(Schema):
    slug: str
    name: str
    claude_md: str
    agents_md: str
    agents: list["AgentSummary"]


# ---------- Agent ----------

class AgentSummary(Schema):
    slug: str
    name: str
    plugin_slug: str = ""


class AgentDetail(Schema):
    slug: str
    name: str
    plugin_slug: str
    content: str


# ---------- Reference ----------

class ReferenceSummary(Schema):
    slug: str
    title: str
    doc_type: str
    file_path: str


class ReferenceDetail(Schema):
    slug: str
    title: str
    doc_type: str
    file_path: str
    plugin_slug: str
    content: str


# ---------- Source ----------

class SourceFileSummary(Schema):
    file_path: str
    language: str
    chunk_count: int = 1


class SourceFileDetail(Schema):
    file_path: str
    ref_library: str
    language: str
    plugin_slug: str
    content: str


class SourceChunkSchema(Schema):
    file_path: str
    ref_library: str
    language: str
    chunk_type: str
    symbol_name: str
    content: str
    start_line: int
    end_line: int


# ---------- Template ----------

class TemplateSummary(Schema):
    slug: str
    name: str
    category: str
    language: str
    file_path: str


class TemplateDetail(Schema):
    slug: str
    name: str
    category: str
    language: str
    file_path: str
    plugin_slug: str
    content: str


# ---------- Search ----------

class SearchRequest(Schema):
    query: str
    plugin: str | None = None
    content_type: str | None = None  # agent, reference, source
    limit: int = 20


class SourceSearchRequest(Schema):
    query: str
    plugin: str | None = None
    ref_library: str | None = None
    language: str | None = None
    limit: int = 20


class SearchResult(Schema):
    content_type: str
    plugin_slug: str
    title: str
    slug: str
    snippet: str
    rank: float = 0.0


# ---------- Admin ----------

class SyncResponse(Schema):
    status: str
    message: str
    run_id: int | None = None


class ErrorResponse(Schema):
    detail: str
