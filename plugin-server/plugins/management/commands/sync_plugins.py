"""
Management command: sync_plugins

Clones/pulls the Plugins-building repo and ingests all plugin content
into the database. Idempotent — uses upserts throughout.

Usage:
    python manage.py sync_plugins [--plugin SLUG] [--skip-embeddings] [--force]
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from plugins.chunkers import chunk_source, detect_language
from plugins.models import (
    AgentDefinition,
    IngestionRun,
    Plugin,
    ReferenceDoc,
    SourceChunk,
    Template,
)

# Directories to skip during plugin discovery
SKIP_DIRS = {
    ".git", "scripts", "skills", "node_modules", "__pycache__",
    ".claude-plugin", "plugin-server",
}

# Known plugin directories (have .claude-plugin/plugin.json)
CONTENT_DIRS = {"agents", "references", "knowledge", "templates", "refs",
                "commands", "data", "examples", "presets", "patterns",
                "product", "math", "skills"}


def _extract_frontmatter_name(content: str) -> str:
    """Extract name from YAML frontmatter if present."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            if line.strip().startswith("name:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


class Command(BaseCommand):
    help = "Sync plugins from the GitHub repo into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--plugin", type=str, default=None,
            help="Only sync a specific plugin by slug",
        )
        parser.add_argument(
            "--skip-embeddings", action="store_true",
            help="Skip embedding generation (Phase 2)",
        )
        parser.add_argument(
            "--force", action="store_true",
            help="Force full re-sync even if no new commits",
        )
        parser.add_argument(
            "--local", type=str, default=None,
            help="Use local repo path instead of cloning",
        )

    def handle(self, *args, **options):
        start = time.time()
        run = IngestionRun.objects.create(
            commit_sha="pending",
            status="running",
        )

        try:
            repo_path = self._get_repo(options)
            commit_sha = self._get_commit_sha(repo_path)
            run.commit_sha = commit_sha
            run.save(update_fields=["commit_sha"])

            plugin_dirs = self._discover_plugins(repo_path, options.get("plugin"))
            self.stdout.write(f"Found {len(plugin_dirs)} plugin(s) to sync")

            total_chunks = 0
            for plugin_dir in plugin_dirs:
                chunks = self._sync_plugin(plugin_dir, repo_path)
                total_chunks += chunks

            run.status = "completed"
            run.plugins_synced = len(plugin_dirs)
            run.chunks_created = total_chunks
            run.duration_seconds = time.time() - start
            run.save()

            self.stdout.write(self.style.SUCCESS(
                f"Synced {len(plugin_dirs)} plugins, {total_chunks} chunks "
                f"in {run.duration_seconds:.1f}s"
            ))

        except Exception as e:
            run.status = "failed"
            run.error_log = str(e)
            run.duration_seconds = time.time() - start
            run.save()
            raise CommandError(f"Sync failed: {e}") from e

    def _get_repo(self, options) -> Path:
        """Clone or pull the repo, or use local path."""
        if options.get("local"):
            path = Path(options["local"])
            if not path.exists():
                raise CommandError(f"Local path does not exist: {path}")
            return path

        clone_dir = settings.REPO_CLONE_DIR
        clone_dir.mkdir(parents=True, exist_ok=True)
        repo_dir = clone_dir / "Plugins-building"

        if repo_dir.exists():
            self.stdout.write("Pulling latest changes...")
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=repo_dir, check=True, capture_output=True,
            )
        else:
            self.stdout.write("Cloning repository...")
            repo_url = f"https://github.com/{settings.GITHUB_REPO}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1",
                 "-c", "GIT_LFS_SKIP_SMUDGE=1",
                 repo_url, str(repo_dir)],
                check=True, capture_output=True,
            )

        return repo_dir

    def _get_commit_sha(self, repo_path: Path) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path, capture_output=True, text=True,
        )
        return result.stdout.strip()[:40] if result.returncode == 0 else "unknown"

    def _discover_plugins(self, repo_path: Path, single: str | None) -> list[Path]:
        """Find plugin directories (those with .claude-plugin/plugin.json)."""
        plugins = []
        for entry in sorted(repo_path.iterdir()):
            if not entry.is_dir() or entry.name in SKIP_DIRS or entry.name.startswith("."):
                continue
            manifest = entry / ".claude-plugin" / "plugin.json"
            if manifest.exists():
                if single and entry.name != single:
                    continue
                plugins.append(entry)
        return plugins

    def _sync_plugin(self, plugin_dir: Path, repo_root: Path) -> int:
        """Sync a single plugin. Returns chunk count."""
        slug = plugin_dir.name
        self.stdout.write(f"  Syncing {slug}...")

        # Load manifest
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        manifest = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())

        # Read CLAUDE.md and AGENTS.md
        claude_md = ""
        claude_md_path = plugin_dir / "CLAUDE.md"
        if claude_md_path.exists():
            claude_md = claude_md_path.read_text()

        agents_md = ""
        agents_md_path = plugin_dir / "AGENTS.md"
        if agents_md_path.exists():
            agents_md = agents_md_path.read_text()

        # Upsert plugin
        plugin, _ = Plugin.all_objects.update_or_create(
            slug=slug,
            defaults={
                "name": manifest.get("name", slug),
                "version": manifest.get("version", "1.0.0"),
                "description": manifest.get("description", ""),
                "claude_md": claude_md,
                "agents_md": agents_md,
                "manifest": manifest,
                "is_deleted": False,
            },
        )

        chunk_count = 0

        # Sync agents
        chunk_count += self._sync_agents(plugin, plugin_dir)

        # Sync references and knowledge
        chunk_count += self._sync_references(plugin, plugin_dir)

        # Sync templates
        chunk_count += self._sync_templates(plugin, plugin_dir)

        # Sync source refs
        chunk_count += self._sync_source_refs(plugin, plugin_dir)

        # Soft-delete orphaned content
        self._cleanup_orphans(plugin, plugin_dir)

        return chunk_count

    def _sync_agents(self, plugin: Plugin, plugin_dir: Path) -> int:
        """Sync agent .md files."""
        agents_dir = plugin_dir / "agents"
        if not agents_dir.exists():
            return 0

        count = 0
        seen_slugs = set()
        for md_file in sorted(agents_dir.glob("*.md")):
            agent_slug = md_file.stem
            seen_slugs.add(agent_slug)
            content = md_file.read_text()
            name = _extract_frontmatter_name(content) or agent_slug.replace("-", " ").title()

            AgentDefinition.all_objects.update_or_create(
                plugin=plugin,
                slug=agent_slug,
                defaults={
                    "name": name,
                    "content": content,
                    "is_deleted": False,
                },
            )
            count += 1

        # Soft-delete agents no longer in repo
        plugin.agents.exclude(slug__in=seen_slugs).update(is_deleted=True)
        return count

    def _sync_references(self, plugin: Plugin, plugin_dir: Path) -> int:
        """Sync references/ and knowledge/ directories."""
        count = 0
        seen_paths = set()

        for dir_name, doc_type in [("references", "reference"), ("knowledge", "knowledge")]:
            ref_dir = plugin_dir / dir_name
            if not ref_dir.exists():
                continue

            for file_path in sorted(ref_dir.rglob("*")):
                if not file_path.is_file():
                    continue
                # Skip binary files and very large files
                if file_path.suffix in (".png", ".jpg", ".gif", ".ico", ".woff", ".woff2"):
                    continue
                try:
                    content = file_path.read_text(errors="replace")
                except Exception:
                    continue

                rel_path = str(file_path.relative_to(plugin_dir))
                seen_paths.add(rel_path)
                ref_slug = slugify(file_path.stem)[:200]

                # Determine title
                title = file_path.stem.replace("-", " ").replace("_", " ").title()

                ReferenceDoc.all_objects.update_or_create(
                    plugin=plugin,
                    file_path=rel_path,
                    defaults={
                        "slug": ref_slug,
                        "title": title,
                        "content": content,
                        "doc_type": doc_type,
                        "is_deleted": False,
                    },
                )
                count += 1

        # Also ingest README.md as a reference
        readme = plugin_dir / "README.md"
        if readme.exists():
            rel_path = "README.md"
            seen_paths.add(rel_path)
            content = readme.read_text()
            ReferenceDoc.all_objects.update_or_create(
                plugin=plugin,
                file_path=rel_path,
                defaults={
                    "slug": "readme",
                    "title": f"{plugin.name} README",
                    "content": content,
                    "doc_type": "readme",
                    "is_deleted": False,
                },
            )
            count += 1

        plugin.references.exclude(file_path__in=seen_paths).update(is_deleted=True)
        return count

    def _sync_templates(self, plugin: Plugin, plugin_dir: Path) -> int:
        """Sync templates/ directory."""
        templates_dir = plugin_dir / "templates"
        if not templates_dir.exists():
            return 0

        count = 0
        seen_paths = set()

        for file_path in sorted(templates_dir.rglob("*")):
            if not file_path.is_file():
                continue
            try:
                content = file_path.read_text(errors="replace")
            except Exception:
                continue

            rel_path = str(file_path.relative_to(plugin_dir))
            seen_paths.add(rel_path)

            # Category is the subdirectory under templates/
            parts = file_path.relative_to(templates_dir).parts
            category = parts[0] if len(parts) > 1 else "default"
            template_slug = slugify(file_path.stem)[:200]
            lang = detect_language(str(file_path))

            Template.all_objects.update_or_create(
                plugin=plugin,
                file_path=rel_path,
                defaults={
                    "slug": template_slug,
                    "name": file_path.stem.replace("-", " ").replace("_", " ").title(),
                    "category": category,
                    "content": content,
                    "language": lang,
                    "is_deleted": False,
                },
            )
            count += 1

        plugin.templates.exclude(file_path__in=seen_paths).update(is_deleted=True)
        return count

    def _sync_source_refs(self, plugin: Plugin, plugin_dir: Path) -> int:
        """Sync refs/ directory with source code chunking."""
        refs_dir = plugin_dir / "refs"
        if not refs_dir.exists():
            return 0

        count = 0
        seen_paths = set()

        for ref_lib_dir in sorted(refs_dir.iterdir()):
            if not ref_lib_dir.is_dir():
                continue
            ref_library = ref_lib_dir.name

            for file_path in sorted(ref_lib_dir.rglob("*")):
                if not file_path.is_file():
                    continue
                # Skip binary and non-source files
                if file_path.suffix in (
                    ".png", ".jpg", ".gif", ".ico", ".woff", ".woff2",
                    ".eot", ".ttf", ".svg", ".map", ".lock", ".min.js",
                ):
                    continue
                # Skip very large files (>500KB)
                if file_path.stat().st_size > 500_000:
                    continue

                try:
                    content = file_path.read_text(errors="replace")
                except Exception:
                    continue

                if not content.strip():
                    continue

                rel_path = str(file_path.relative_to(plugin_dir))
                language = detect_language(str(file_path))

                # Chunk the source
                chunks = chunk_source(content, str(file_path))

                # Delete existing chunks for this file (full replace)
                SourceChunk.all_objects.filter(
                    plugin=plugin, file_path=rel_path
                ).delete()

                for chunk in chunks:
                    SourceChunk.objects.create(
                        plugin=plugin,
                        file_path=rel_path,
                        ref_library=ref_library,
                        language=language,
                        chunk_type=chunk.chunk_type,
                        symbol_name=chunk.symbol_name,
                        content=chunk.content,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                    )
                    count += 1
                    seen_paths.add(rel_path)

        # Soft-delete chunks for files no longer in repo
        plugin.source_chunks.exclude(file_path__in=seen_paths).update(is_deleted=True)
        return count

    def _cleanup_orphans(self, plugin: Plugin, plugin_dir: Path):
        """Soft-delete any content whose source files no longer exist."""
        # Already handled per-type in the sync methods above
        pass
