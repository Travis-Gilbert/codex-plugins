from django.db import models

from core.models import TimestampedModel


class Plugin(TimestampedModel):
    """
    One row per plugin directory in the repo.
    slug is the directory name (e.g., "d3-pro", "django-engine-pro").
    """

    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=20, default="1.0.0")
    description = models.TextField(blank=True)
    claude_md = models.TextField(blank=True, help_text="Full CLAUDE.md content")
    agents_md = models.TextField(blank=True, help_text="Full AGENTS.md content")
    manifest = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contents of .claude-plugin/plugin.json",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.version})"


class AgentDefinition(TimestampedModel):
    """One row per agent .md file."""

    plugin = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name="agents"
    )
    slug = models.SlugField(max_length=100)
    name = models.CharField(max_length=200)
    content = models.TextField()
    # Phase 2: embedding = VectorField(dimensions=1536, null=True, blank=True)

    class Meta:
        unique_together = [("plugin", "slug")]
        indexes = [models.Index(fields=["plugin", "slug"])]

    def __str__(self):
        return f"{self.plugin.slug}/{self.slug}"


class ReferenceDoc(TimestampedModel):
    """Curated knowledge from references/ and knowledge/ directories."""

    plugin = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name="references"
    )
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=300)
    content = models.TextField()
    file_path = models.CharField(
        max_length=500,
        help_text="Path relative to plugin root",
    )
    doc_type = models.CharField(
        max_length=50,
        db_index=True,
        choices=[
            ("reference", "Reference Doc"),
            ("knowledge", "Knowledge File"),
            ("skill", "Skill Definition"),
            ("readme", "README"),
        ],
    )
    # Phase 2: embedding = VectorField(dimensions=1536, null=True, blank=True)

    class Meta:
        unique_together = [("plugin", "file_path")]
        indexes = [models.Index(fields=["plugin", "doc_type"])]

    def __str__(self):
        return f"{self.plugin.slug}/{self.file_path}"


class SourceChunk(TimestampedModel):
    """
    Chunked source code from refs/ directories.
    """

    plugin = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name="source_chunks"
    )
    file_path = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Path relative to plugin root",
    )
    ref_library = models.CharField(max_length=200, db_index=True)
    language = models.CharField(
        max_length=30,
        db_index=True,
        choices=[
            ("javascript", "JavaScript"),
            ("typescript", "TypeScript"),
            ("python", "Python"),
            ("markdown", "Markdown"),
            ("json", "JSON"),
            ("other", "Other"),
        ],
    )
    chunk_type = models.CharField(
        max_length=30,
        choices=[
            ("function", "Function"),
            ("class", "Class"),
            ("module", "Module/File"),
            ("section", "Markdown Section"),
            ("config", "Configuration"),
        ],
    )
    symbol_name = models.CharField(max_length=200, blank=True, db_index=True)
    content = models.TextField()
    start_line = models.IntegerField(default=0)
    end_line = models.IntegerField(default=0)
    # Phase 2: embedding = VectorField(dimensions=1536, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["plugin", "ref_library"]),
            models.Index(fields=["plugin", "language"]),
            models.Index(fields=["ref_library", "symbol_name"]),
        ]

    def __str__(self):
        label = self.symbol_name or self.chunk_type
        return f"{self.plugin.slug}/{self.file_path}::{label}"


class Template(TimestampedModel):
    """Complete, copy-paste-ready scaffolds from templates/ directories."""

    plugin = models.ForeignKey(
        Plugin, on_delete=models.CASCADE, related_name="templates"
    )
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=300)
    category = models.CharField(
        max_length=100, help_text="Template subdirectory"
    )
    file_path = models.CharField(max_length=500)
    content = models.TextField()
    language = models.CharField(max_length=30, default="python")

    class Meta:
        unique_together = [("plugin", "file_path")]

    def __str__(self):
        return f"{self.plugin.slug}/{self.file_path}"


class IngestionRun(TimestampedModel):
    """Tracks each sync from GitHub."""

    commit_sha = models.CharField(max_length=40)
    status = models.CharField(
        max_length=20,
        choices=[
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
    )
    plugins_synced = models.IntegerField(default=0)
    chunks_created = models.IntegerField(default=0)
    embeddings_generated = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sync {self.commit_sha[:8]} ({self.status})"
