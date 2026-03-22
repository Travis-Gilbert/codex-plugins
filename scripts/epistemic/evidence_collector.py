"""Stage 1: Evidence Collector.

Reads session logs and classifies outcomes for each claim referenced
in those sessions. Produces EvidenceRecord objects that the confidence
updater consumes.

Evidence sources:
  1. Session logs (knowledge/session_log/*.jsonl) — direct observation
  2. Git diffs (optional) — matches suggestions to commits by file proximity

Evidence classification:
  - accepted: suggestion was applied (suggestion_outcome == "accepted")
  - modified: suggestion was partially applied (outcome == "modified")
  - rejected: suggestion was explicitly rejected (outcome == "rejected")
  - abandoned: suggestion was never acted on (outcome == "abandoned")
  - consulted: claim was consulted but no suggestion linked to it
  - not_consulted: claim is active and tagged for this domain but was not
    consulted (weak negative signal)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .config import (
    CLAIMS_FILE,
    MANIFEST_FILE,
    SESSION_LOG_DIR,
    knowledge_path,
)


# ---------------------------------------------------------------------------
# Evidence record
# ---------------------------------------------------------------------------

@dataclass
class EvidenceRecord:
    """A single piece of evidence about a claim from a session."""
    claim_id: str
    outcome: str  # accepted, modified, rejected, abandoned, consulted, not_consulted
    session_file: str
    project: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "outcome": self.outcome,
            "session_file": self.session_file,
            "project": self.project,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Session log processing
# ---------------------------------------------------------------------------

@dataclass
class SessionSummary:
    """Parsed summary of a single session log."""
    file: Path
    project: str = ""
    agents_invoked: list[str] = field(default_factory=list)
    claims_consulted: set[str] = field(default_factory=set)
    suggestions: dict[str, dict] = field(default_factory=dict)  # sug_id -> event
    outcomes: dict[str, str] = field(default_factory=dict)  # sug_id -> outcome
    suggestion_claims: dict[str, list[str]] = field(default_factory=dict)  # sug_id -> claim_ids
    tensions: list[dict] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    timestamp: str = ""


def parse_session_log(filepath: Path) -> SessionSummary:
    """Parse a session log file into a structured summary."""
    summary = SessionSummary(file=filepath)

    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        event = json.loads(line)
        etype = event.get("event", "")

        if etype == "session_start":
            summary.project = event.get("project", "")
            summary.timestamp = event.get("timestamp", "")

        elif etype == "agent_invoked":
            summary.agents_invoked.append(event.get("agent", ""))

        elif etype == "claim_consulted":
            cid = event.get("claim_id", "")
            if cid:
                summary.claims_consulted.add(cid)

        elif etype == "suggestion":
            sid = event.get("suggestion_id", "")
            if sid:
                summary.suggestions[sid] = event
                summary.suggestion_claims[sid] = event.get("claim_refs", [])

        elif etype == "suggestion_outcome":
            sid = event.get("suggestion_id", "")
            if sid:
                summary.outcomes[sid] = event.get("outcome", "")

        elif etype == "tension_surfaced":
            summary.tensions.append(event)

        elif etype == "candidate_claim":
            summary.candidates.append(event)

    return summary


# ---------------------------------------------------------------------------
# Evidence extraction
# ---------------------------------------------------------------------------

def extract_evidence(
    plugin_name: str,
    since: str | None = None,
) -> list[EvidenceRecord]:
    """Extract evidence records from unprocessed session logs.

    Args:
        plugin_name: Plugin to process.
        since: ISO date string. Only process sessions after this date.
               If None, processes all sessions.

    Returns:
        List of EvidenceRecord objects.
    """
    kpath = knowledge_path(plugin_name)
    log_dir = kpath / SESSION_LOG_DIR
    if not log_dir.exists():
        return []

    # Load active claim IDs and their domains for not_consulted detection
    claims_file = kpath / CLAIMS_FILE
    active_claims: dict[str, dict] = {}  # id -> {domain, tags}
    if claims_file.exists():
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                claim = json.loads(line)
                if claim.get("status") == "active":
                    active_claims[claim["id"]] = {
                        "domain": claim.get("domain", ""),
                        "tags": claim.get("tags", []),
                    }

    # Determine last processed timestamp
    if since is None:
        manifest_file = kpath / MANIFEST_FILE
        if manifest_file.exists():
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            # Use last update as the since marker
            since = manifest.get("last_updated", "")

    records: list[EvidenceRecord] = []

    for log_file in sorted(log_dir.glob("*.jsonl")):
        # Skip files older than since marker (filename is timestamp-based)
        if since and log_file.stem < since.replace("-", "").replace(":", "").replace("T", "T")[:15]:
            continue

        summary = parse_session_log(log_file)
        session_file = log_file.name

        # 1. Claims with explicit suggestion outcomes
        for sug_id, outcome in summary.outcomes.items():
            claim_refs = summary.suggestion_claims.get(sug_id, [])
            for cid in claim_refs:
                records.append(EvidenceRecord(
                    claim_id=cid,
                    outcome=outcome,
                    session_file=session_file,
                    project=summary.project,
                    timestamp=summary.timestamp,
                ))

        # 2. Claims consulted but not linked to any suggestion
        claims_with_suggestions = set()
        for refs in summary.suggestion_claims.values():
            claims_with_suggestions.update(refs)

        for cid in summary.claims_consulted - claims_with_suggestions:
            records.append(EvidenceRecord(
                claim_id=cid,
                outcome="consulted",
                session_file=session_file,
                project=summary.project,
                timestamp=summary.timestamp,
            ))

        # 3. Active claims not consulted (weak negative signal)
        # Only apply this if the session actually consulted some claims
        # (otherwise the knowledge system wasn't active in this session)
        if summary.claims_consulted and active_claims:
            # Determine which domains were relevant to this session
            session_domains = set()
            for cid in summary.claims_consulted:
                if cid in active_claims:
                    domain = active_claims[cid]["domain"]
                    # Include the base domain (e.g., "django" from "django.models")
                    parts = domain.split(".")
                    for i in range(len(parts)):
                        session_domains.add(".".join(parts[:i + 1]))

            for cid, info in active_claims.items():
                if cid in summary.claims_consulted:
                    continue
                # Only penalize claims in the same domain family
                claim_domain = info["domain"]
                if any(claim_domain.startswith(sd) for sd in session_domains):
                    records.append(EvidenceRecord(
                        claim_id=cid,
                        outcome="not_consulted",
                        session_file=session_file,
                        project=summary.project,
                        timestamp=summary.timestamp,
                    ))

    return records


def collect_evidence(plugin_name: str, since: str | None = None) -> list[dict]:
    """Collect and return evidence as dicts (for pipeline integration)."""
    records = extract_evidence(plugin_name, since=since)
    return [r.to_dict() for r in records]
