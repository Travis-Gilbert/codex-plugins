"""Stage 3: Pattern Extractor.

Discovers recurring patterns from session logs and git diffs using
SBERT embeddings + HDBSCAN clustering.

For each cluster with 3+ members, proposes a new Claim or Method
as a draft for human review.

This module handles two types of pattern discovery:

1. Session suggestion clustering — groups similar suggestions from
   session logs to find recurring advice patterns.
2. (Future) Git diff clustering — groups similar code changes to
   discover implicit coding patterns.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np

from .config import (
    CLAIMS_FILE,
    SESSION_LOG_DIR,
    knowledge_path,
)
from .schema import Claim, claim_id as make_id


# ---------------------------------------------------------------------------
# Clustering configuration
# ---------------------------------------------------------------------------

MIN_CLUSTER_SIZE = 3  # minimum members to propose a claim
MIN_SAMPLES = 2  # HDBSCAN min_samples parameter


# ---------------------------------------------------------------------------
# Session-based pattern discovery
# ---------------------------------------------------------------------------

def _collect_suggestion_texts(plugin_name: str) -> list[dict]:
    """Collect all suggestion events from session logs."""
    kpath = knowledge_path(plugin_name)
    log_dir = kpath / SESSION_LOG_DIR
    if not log_dir.exists():
        return []

    suggestions = []
    for log_file in sorted(log_dir.glob("*.jsonl")):
        for line in log_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event") == "suggestion":
                suggestions.append({
                    "text": f"{event.get('suggestion_type', '')} in {event.get('file', '')}",
                    "file": event.get("file", ""),
                    "type": event.get("suggestion_type", ""),
                    "claim_refs": event.get("claim_refs", []),
                    "session": log_file.name,
                })

    return suggestions


def extract_patterns(plugin_name: str) -> list[Claim]:
    """Discover patterns from session suggestion clustering.

    Returns draft Claim objects for human review.
    """
    suggestions = _collect_suggestion_texts(plugin_name)

    if len(suggestions) < MIN_CLUSTER_SIZE:
        return []

    # Embed suggestion texts
    from .embedding_manager import embed_texts

    texts = [s["text"] for s in suggestions]
    embeddings = embed_texts(texts)

    # Cluster with HDBSCAN
    try:
        import hdbscan
    except ImportError:
        print("  hdbscan not installed, skipping pattern extraction", file=sys.stderr)
        return []

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=MIN_SAMPLES,
        metric="euclidean",
    )
    labels = clusterer.fit_predict(embeddings)

    # Analyze clusters
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    if n_clusters == 0:
        return []

    print(f"  Found {n_clusters} suggestion clusters", file=sys.stderr)

    # Load existing claim texts to check for duplicates
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    existing_texts: set[str] = set()
    if claims_file.exists():
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_texts.add(json.loads(line).get("text", "").lower().strip())

    proposed_claims: list[Claim] = []
    today = date.today().isoformat()

    for cluster_id in range(n_clusters):
        members = [i for i, l in enumerate(labels) if l == cluster_id]
        if len(members) < MIN_CLUSTER_SIZE:
            continue

        # Analyze the cluster
        cluster_suggestions = [suggestions[i] for i in members]
        file_types = Counter(s["file"].split(".")[-1] if "." in s["file"] else "unknown"
                            for s in cluster_suggestions)
        suggestion_types = Counter(s["type"] for s in cluster_suggestions)
        claim_refs = set()
        for s in cluster_suggestions:
            claim_refs.update(s["claim_refs"])

        # Generate a description for the cluster
        most_common_type = suggestion_types.most_common(1)[0][0] if suggestion_types else "pattern"
        most_common_ext = file_types.most_common(1)[0][0] if file_types else "files"

        description = (
            f"Recurring {most_common_type} pattern in .{most_common_ext} files "
            f"(observed {len(members)} times across "
            f"{len(set(s['session'] for s in cluster_suggestions))} sessions)"
        )

        # Skip if too similar to existing
        if description.lower().strip() in existing_texts:
            continue

        cid = make_id(plugin_name, f"pattern-{cluster_id}-{description}")
        proposed_claims.append(Claim(
            id=cid,
            text=description,
            domain=plugin_name,
            agent_source="pattern_extractor",
            type="empirical",
            source=f"HDBSCAN cluster {cluster_id} ({len(members)} members)",
            first_seen=today,
            last_validated=today,
            status="draft",
            tags=list(file_types.keys())[:5],
            related_claims=list(claim_refs)[:5],
        ))

    return proposed_claims


def save_pattern_claims(plugin_name: str, claims: list[Claim]) -> int:
    """Append pattern-discovered claims to claims.jsonl. Returns count saved."""
    if not claims:
        return 0

    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE

    existing_ids: set[str] = set()
    if claims_file.exists():
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_ids.add(json.loads(line).get("id", ""))

    saved = 0
    with open(claims_file, "a", encoding="utf-8") as f:
        for claim in claims:
            if claim.id not in existing_ids:
                f.write(claim.model_dump_json() + "\n")
                saved += 1

    return saved
