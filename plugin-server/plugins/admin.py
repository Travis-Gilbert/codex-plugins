from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    AgentDefinition,
    IngestionRun,
    Plugin,
    ReferenceDoc,
    SourceChunk,
    Template,
)


@admin.register(Plugin)
class PluginAdmin(ModelAdmin):
    list_display = ["name", "slug", "version", "is_deleted"]
    list_filter = ["is_deleted"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class AgentInline(admin.TabularInline):
    model = AgentDefinition
    extra = 0
    fields = ["slug", "name"]
    readonly_fields = ["slug", "name"]


@admin.register(AgentDefinition)
class AgentDefinitionAdmin(ModelAdmin):
    list_display = ["__str__", "name", "plugin"]
    list_filter = ["plugin"]
    search_fields = ["name", "slug", "content"]


@admin.register(ReferenceDoc)
class ReferenceDocAdmin(ModelAdmin):
    list_display = ["__str__", "doc_type", "plugin"]
    list_filter = ["plugin", "doc_type"]
    search_fields = ["title", "slug", "content"]


@admin.register(SourceChunk)
class SourceChunkAdmin(ModelAdmin):
    list_display = ["__str__", "ref_library", "language", "chunk_type"]
    list_filter = ["plugin", "ref_library", "language", "chunk_type"]
    search_fields = ["symbol_name", "file_path", "content"]


@admin.register(Template)
class TemplateAdmin(ModelAdmin):
    list_display = ["__str__", "category", "language", "plugin"]
    list_filter = ["plugin", "category", "language"]
    search_fields = ["name", "slug", "content"]


@admin.register(IngestionRun)
class IngestionRunAdmin(ModelAdmin):
    list_display = [
        "commit_sha",
        "status",
        "plugins_synced",
        "chunks_created",
        "duration_seconds",
        "created_at",
    ]
    list_filter = ["status"]
    readonly_fields = [
        "commit_sha",
        "status",
        "plugins_synced",
        "chunks_created",
        "embeddings_generated",
        "error_log",
        "duration_seconds",
    ]
