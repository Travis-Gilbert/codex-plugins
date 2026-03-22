"""Extract claims from plugin markdown files and write to knowledge/claims.jsonl.

Usage:
    python -m scripts.epistemic.seed_knowledge django-design
    python -m scripts.epistemic.seed_knowledge django-design --dry-run
    python -m scripts.epistemic.seed_knowledge --all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from .config import (
    AGENT_DOMAIN_MAP,
    AGENT_GLOB,
    CLAUDE_MD,
    HEADING_DOMAIN_MAP,
    HEURISTIC_MARKERS,
    IMPERATIVE_MARKERS,
    INITIAL_STATUS,
    MAX_CLAIM_LENGTH,
    MIN_CLAIM_LENGTH,
    PLUGINS,
    SKILL_GLOB,
    knowledge_path,
    plugin_path,
)
from .schema import Claim, Manifest, ManifestStats, UpdateLogEntry, claim_id


# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------

def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter delimited by --- ... ---."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


def is_inside_code_fence(lines: list[str], line_idx: int) -> bool:
    """Check if a line is inside a fenced code block."""
    fence_count = 0
    for i in range(line_idx):
        if lines[i].strip().startswith("```"):
            fence_count += 1
    return fence_count % 2 == 1


def clean_claim_text(text: str) -> str:
    """Strip markdown formatting from a claim string."""
    # Remove leading bullet markers
    text = re.sub(r"^[-*]\s+", "", text.strip())
    # Remove leading numbered list markers
    text = re.sub(r"^\d+\.\s+", "", text)
    # Remove bold markers
    text = text.replace("**", "")
    # Remove inline code backticks (keep the content)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_structural_line(text: str) -> bool:
    """Return True if a line is purely structural markdown (not a real claim)."""
    cleaned = text.strip().strip("-*").strip()
    # Bold-only lines like "- **models.py**"
    if re.match(r"^\*\*[^*]+\*\*:?$", cleaned):
        return True
    # Very short lines that are just labels
    if len(cleaned) < MIN_CLAIM_LENGTH:
        return True
    # File path references (structural metadata, not domain knowledge)
    if re.match(r"^[`.]?[\w./\-]+[`]?\s*[—–-]\s+", cleaned):
        return True
    # Lines that are just listing files/directories
    if re.match(r"^(commands|agents|skills|templates|refs|references)/", cleaned):
        return True
    # Lines describing plugin structure (e.g., "5 agents: ..." or "Plugin manifest")
    if re.search(r"\d+\s+(agents?|commands?|skills?|reference files?)", cleaned.lower()):
        return True
    # Lines referencing file extensions or paths as primary content
    if cleaned.count("/") >= 2 and len(cleaned) < 80:
        return True
    return False


# ---------------------------------------------------------------------------
# Heading context tracker
# ---------------------------------------------------------------------------

class HeadingTracker:
    """Track markdown heading hierarchy to assign domain context."""

    def __init__(self, base_domain: str):
        self.base_domain = base_domain
        self._stack: list[tuple[int, str]] = []  # (level, heading_text)
        self._severity: str | None = None

    def update(self, line: str) -> None:
        """Process a heading line and update the stack."""
        match = re.match(r"^(#{1,6})\s+(.+)", line)
        if not match:
            return
        level = len(match.group(1))
        heading = match.group(2).strip()

        # Pop headings at same or deeper level
        self._stack = [(l, h) for l, h in self._stack if l < level]
        self._stack.append((level, heading))

        # Track severity context
        heading_lower = heading.lower()
        if "critical" in heading_lower:
            self._severity = "critical"
        elif "warning" in heading_lower:
            self._severity = "warning"
        elif "info" in heading_lower:
            self._severity = "info"

    @property
    def severity(self) -> str | None:
        return self._severity

    @property
    def domain(self) -> str:
        """Compute the current domain from the heading stack."""
        subdomain_parts: list[str] = []
        for _, heading in self._stack:
            heading_lower = heading.lower()
            for keyword, subdomain in HEADING_DOMAIN_MAP.items():
                if keyword.lower() in heading_lower:
                    subdomain_parts = subdomain.split(".")
                    break

        if subdomain_parts:
            # Avoid duplicating the base domain prefix
            base_parts = self.base_domain.split(".")
            # Find the first subdomain part not already in base
            unique_parts = []
            for part in subdomain_parts:
                if part not in base_parts:
                    unique_parts.append(part)
            if unique_parts:
                return f"{self.base_domain}.{'.'.join(unique_parts)}"
        return self.base_domain


# ---------------------------------------------------------------------------
# Claim type classifier
# ---------------------------------------------------------------------------

def classify_claim_type(
    text: str,
    severity: str | None,
    source_type: str,
) -> str:
    """Assign a claim type based on heuristics."""
    text_lower = text.lower()

    # Source-based classification
    if source_type == "principle":
        return "architectural_rule"
    if source_type == "convention":
        return "preference"

    # Severity-based classification (from agent checklists)
    if severity in ("critical", "warning"):
        return "best_practice"
    if severity == "info":
        return "heuristic"

    # Keyword-based classification
    for marker in HEURISTIC_MARKERS:
        if marker in text_lower:
            return "heuristic"

    for marker in IMPERATIVE_MARKERS[:4]:  # always, never, must, should
        if text_lower.startswith(marker) or f" {marker} " in text_lower:
            return "best_practice"

    return "best_practice"


# ---------------------------------------------------------------------------
# Tag extraction
# ---------------------------------------------------------------------------

# Common Django/tech keywords to match as tags
TAG_KEYWORDS = [
    "orm", "queryset", "select_related", "prefetch_related", "index",
    "n+1", "models", "views", "settings", "admin", "forms", "urls",
    "templates", "htmx", "alpine", "cotton", "csrf", "security",
    "performance", "migration", "serializer", "viewset", "permission",
    "pagination", "d3", "tailwind", "design token", "responsive",
    "accessibility", "a11y", "wcag", "aria", "keyboard",
    "animation", "motion", "spring", "scroll", "gesture",
    "pytorch", "gnn", "training", "loss", "gradient", "checkpoint",
    "transformer", "attention", "embedding", "fine-tune", "lora",
]


def extract_tags(text: str) -> list[str]:
    """Extract relevant tags from claim text."""
    text_lower = text.lower()
    return [tag for tag in TAG_KEYWORDS if tag in text_lower]


# ---------------------------------------------------------------------------
# Extraction from a single markdown file
# ---------------------------------------------------------------------------

def extract_claims_from_file(
    filepath: Path,
    plugin_name: str,
    agent_name: str,
    source_type: str = "checklist",
) -> list[Claim]:
    """Extract claims from a single markdown file."""
    text = filepath.read_text(encoding="utf-8")
    text = strip_frontmatter(text)
    lines = text.split("\n")

    base_domain = AGENT_DOMAIN_MAP.get(agent_name, plugin_name)
    tracker = HeadingTracker(base_domain)
    claims: list[Claim] = []
    today = date.today().isoformat()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Update heading context
        if stripped.startswith("#"):
            tracker.update(stripped)
            continue

        # Skip code fences
        if is_inside_code_fence(lines, i):
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Pattern 1: Checklist items (bullets)
        if re.match(r"^[-*]\s+", stripped):
            raw_text = clean_claim_text(stripped)
            if is_structural_line(stripped) or len(raw_text) < MIN_CLAIM_LENGTH:
                continue
            if len(raw_text) > MAX_CLAIM_LENGTH:
                raw_text = raw_text[:MAX_CLAIM_LENGTH].rsplit(" ", 1)[0] + "..."

            cid = claim_id(plugin_name, raw_text)
            claims.append(Claim(
                id=cid,
                text=raw_text,
                domain=tracker.domain,
                agent_source=agent_name,
                type=classify_claim_type(raw_text, tracker.severity, "checklist"),
                source=f"{filepath.name}:{i + 1}",
                first_seen=today,
                last_validated=today,
                status=INITIAL_STATUS,
                tags=extract_tags(raw_text),
            ))
            continue

        # Pattern 2: Numbered principles (e.g., "1. **Fat models, thin views.**")
        principle_match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*\.?\s*(.*)", stripped)
        if principle_match and source_type in ("principle", "checklist"):
            title = principle_match.group(1)
            explanation = principle_match.group(2).strip()
            raw_text = f"{title}. {explanation}" if explanation else title
            raw_text = clean_claim_text(raw_text)

            if len(raw_text) < MIN_CLAIM_LENGTH:
                continue
            if len(raw_text) > MAX_CLAIM_LENGTH:
                raw_text = raw_text[:MAX_CLAIM_LENGTH].rsplit(" ", 1)[0] + "..."

            cid = claim_id(plugin_name, raw_text)
            claims.append(Claim(
                id=cid,
                text=raw_text,
                domain=tracker.domain,
                agent_source=agent_name,
                type=classify_claim_type(raw_text, tracker.severity, "principle"),
                source=f"{filepath.name}:{i + 1}",
                first_seen=today,
                last_validated=today,
                status=INITIAL_STATUS,
                tags=extract_tags(raw_text),
            ))
            continue

        # Pattern 3: Imperative sentences in prose
        if source_type in ("convention", "checklist"):
            sentence_lower = stripped.lower()
            for marker in IMPERATIVE_MARKERS:
                if sentence_lower.startswith(marker) or sentence_lower.startswith(f"- {marker}"):
                    raw_text = clean_claim_text(stripped)
                    if len(raw_text) < MIN_CLAIM_LENGTH:
                        break
                    if len(raw_text) > MAX_CLAIM_LENGTH:
                        raw_text = raw_text[:MAX_CLAIM_LENGTH].rsplit(" ", 1)[0] + "..."

                    cid = claim_id(plugin_name, raw_text)
                    claims.append(Claim(
                        id=cid,
                        text=raw_text,
                        domain=tracker.domain,
                        agent_source=agent_name,
                        type=classify_claim_type(raw_text, tracker.severity, "convention"),
                        source=f"{filepath.name}:{i + 1}",
                        first_seen=today,
                        last_validated=today,
                        status=INITIAL_STATUS,
                        tags=extract_tags(raw_text),
                    ))
                    break

    return claims


# ---------------------------------------------------------------------------
# Seed a full plugin
# ---------------------------------------------------------------------------

def seed_plugin(plugin_name: str, dry_run: bool = False) -> list[Claim]:
    """Extract all claims from a plugin's markdown files."""
    ppath = plugin_path(plugin_name)
    all_claims: list[Claim] = []
    seen_ids: set[str] = set()

    def add_claims(claims: list[Claim]) -> None:
        for claim in claims:
            if claim.id not in seen_ids:
                seen_ids.add(claim.id)
                all_claims.append(claim)

    # 1. Agent files
    for agent_file in sorted(ppath.glob(AGENT_GLOB)):
        agent_name = agent_file.stem
        claims = extract_claims_from_file(agent_file, plugin_name, agent_name, "checklist")
        add_claims(claims)

    # 2. Skill files
    for skill_file in sorted(ppath.glob(SKILL_GLOB)):
        skill_name = skill_file.parent.name
        claims = extract_claims_from_file(skill_file, plugin_name, skill_name, "principle")
        add_claims(claims)

    # 3. CLAUDE.md
    claude_md = ppath / CLAUDE_MD
    if claude_md.exists():
        claims = extract_claims_from_file(claude_md, plugin_name, "CLAUDE.md", "convention")
        add_claims(claims)

    if dry_run:
        for claim in all_claims:
            print(claim.model_dump_json())
        print(f"\n--- {len(all_claims)} claims extracted from {plugin_name} (dry run) ---",
              file=sys.stderr)
        return all_claims

    # Write claims.jsonl
    kpath = knowledge_path(plugin_name)
    kpath.mkdir(parents=True, exist_ok=True)

    # Load existing IDs to avoid duplicates on re-run
    claims_file = kpath / "claims.jsonl"
    existing_ids: set[str] = set()
    if claims_file.exists():
        for line in claims_file.read_text().splitlines():
            if line.strip():
                existing_ids.add(json.loads(line)["id"])

    new_claims = [c for c in all_claims if c.id not in existing_ids]

    with open(claims_file, "a") as f:
        for claim in new_claims:
            f.write(claim.model_dump_json() + "\n")

    # Create empty JSONL files if they don't exist
    for filename in ["tensions.jsonl", "methods.jsonl", "questions.jsonl", "preferences.jsonl"]:
        fpath = kpath / filename
        if not fpath.exists():
            fpath.touch()

    # Write/update manifest
    total_claims = len(existing_ids) + len(new_claims)
    manifest = Manifest(
        plugin=plugin_name,
        last_updated=date.today().isoformat(),
        stats=ManifestStats(
            total_claims=total_claims,
            draft_claims=total_claims,  # all start as draft
            active_claims=0,
        ),
        update_log=[UpdateLogEntry(
            date=date.today().isoformat(),
            action="seed",
            details=f"Extracted {len(new_claims)} new claims ({total_claims} total)",
        )],
    )
    manifest_file = kpath / "manifest.json"
    manifest_file.write_text(manifest.model_dump_json(indent=2) + "\n")

    print(f"Seeded {plugin_name}: {len(new_claims)} new claims "
          f"({total_claims} total) -> {claims_file}", file=sys.stderr)

    return all_claims


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract knowledge claims from plugin markdown files",
    )
    parser.add_argument(
        "plugin",
        nargs="?",
        choices=list(PLUGINS.keys()),
        help="Plugin to seed (omit with --all to seed everything)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Seed all plugins",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print claims to stdout without writing files",
    )

    args = parser.parse_args()

    if args.all:
        for name in PLUGINS:
            ppath = plugin_path(name)
            if ppath.exists():
                seed_plugin(name, dry_run=args.dry_run)
            else:
                print(f"Skipping {name}: directory not found at {ppath}", file=sys.stderr)
    elif args.plugin:
        seed_plugin(args.plugin, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
