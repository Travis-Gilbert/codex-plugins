"""Stage 4: Tension Detector.

Finds contradictions and conflicts between claims using two methods:

1. Evidence-based: Same claim accepted in one project, rejected in another
2. Semantic-based: Claims with high embedding similarity but opposite advice

Note on numpy .npz loading: allow_pickle=True is required for object arrays
(claim_ids stored as strings). These files are created by our own
embedding_manager — they are trusted, self-generated data.

Outputs new Tension records to knowledge/tensions.jsonl.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

from .config import CLAIMS_FILE, TENSIONS_FILE, knowledge_path
from .schema import Tension, claim_id as make_id


# ---------------------------------------------------------------------------
# Evidence-based tension detection
# ---------------------------------------------------------------------------

def detect_evidence_tensions(
    plugin_name: str,
    evidence: list[dict],
) -> list[Tension]:
    """Find claims with contradictory outcomes across projects."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE

    if not claims_file.exists():
        return []

    claims_by_id = {}
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            claims_by_id[c["id"]] = c

    # Group evidence by claim_id and project
    claim_project_outcomes: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for record in evidence:
        cid = record.get("claim_id", "")
        project = record.get("project", "unknown")
        outcome = record.get("outcome", "")
        if cid and outcome in ("accepted", "rejected", "modified"):
            claim_project_outcomes[cid][project].append(outcome)

    tensions = []
    today = date.today().isoformat()

    for cid, projects in claim_project_outcomes.items():
        if len(projects) < 2:
            continue

        accepting_projects = [p for p, outcomes in projects.items() if "accepted" in outcomes]
        rejecting_projects = [p for p, outcomes in projects.items() if "rejected" in outcomes]

        if accepting_projects and rejecting_projects:
            claim = claims_by_id.get(cid, {})
            tid = make_id(plugin_name, f"tension-evidence-{cid}")
            tensions.append(Tension(
                id=tid,
                claim_a=cid,
                claim_b=cid,
                description=(
                    f"Claim '{claim.get('text', cid)[:80]}...' accepted in "
                    f"{', '.join(accepting_projects)} but rejected in "
                    f"{', '.join(rejecting_projects)}"
                ),
                domain=claim.get("domain", plugin_name),
                status="unresolved",
                context_dependent=True,
                context_note="May be valid in some project contexts but not others",
                occurrences=sum(len(o) for o in projects.values()),
                first_seen=today,
            ))

    return tensions


# ---------------------------------------------------------------------------
# Semantic tension detection
# ---------------------------------------------------------------------------

NEGATION_PAIRS = [
    (r"\balways\b", r"\bnever\b"),
    (r"\buse\b", r"\bavoid\b"),
    (r"\bprefer\b", r"\bavoid\b"),
    (r"\bdo\b", r"\bdo not\b"),
    (r"\bshould\b", r"\bshould not\b"),
    (r"\bmust\b", r"\bmust not\b"),
    (r"\brequire\b", r"\bforbid\b"),
]


def _texts_are_contradictory(text_a: str, text_b: str) -> bool:
    """Heuristic check for contradictory advice between two claim texts."""
    a_lower = text_a.lower()
    b_lower = text_b.lower()

    for pos_pattern, neg_pattern in NEGATION_PAIRS:
        a_has_pos = bool(re.search(pos_pattern, a_lower))
        a_has_neg = bool(re.search(neg_pattern, a_lower))
        b_has_pos = bool(re.search(pos_pattern, b_lower))
        b_has_neg = bool(re.search(neg_pattern, b_lower))

        if (a_has_pos and b_has_neg) or (a_has_neg and b_has_pos):
            return True

    return False


def detect_semantic_tensions(
    plugin_name: str,
    similarity_threshold: float = 0.75,
) -> list[Tension]:
    """Find semantically similar but potentially contradictory claim pairs."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    npz_file = kpath / "embeddings.npz"

    if not claims_file.exists() or not npz_file.exists():
        return []

    claims = []
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            claims.append(json.loads(line))

    # Load our own self-generated embeddings file
    data = np.load(npz_file, allow_pickle=True)
    embeddings = data["embeddings"]
    npz_ids = [str(c) for c in data["claim_ids"]]

    if len(claims) < 2:
        return []

    claims_by_id = {c["id"]: c for c in claims}

    # Pairwise cosine similarity (upper triangle only)
    norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
    sim_matrix = norms @ norms.T

    # Load existing tension pairs to avoid duplicates
    tensions_file = kpath / TENSIONS_FILE
    existing_pairs: set[tuple[str, str]] = set()
    if tensions_file.exists():
        for line in tensions_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                t = json.loads(line)
                pair = tuple(sorted([t.get("claim_a", ""), t.get("claim_b", "")]))
                existing_pairs.add(pair)

    tensions = []
    today = date.today().isoformat()

    for i in range(len(npz_ids)):
        for j in range(i + 1, len(npz_ids)):
            sim = float(sim_matrix[i, j])
            if sim < similarity_threshold:
                continue

            cid_a = npz_ids[i]
            cid_b = npz_ids[j]

            pair = tuple(sorted([cid_a, cid_b]))
            if pair in existing_pairs:
                continue

            claim_a = claims_by_id.get(cid_a, {})
            claim_b = claims_by_id.get(cid_b, {})
            text_a = claim_a.get("text", "")
            text_b = claim_b.get("text", "")

            if not _texts_are_contradictory(text_a, text_b):
                continue

            tid = make_id(plugin_name, f"tension-semantic-{cid_a}-{cid_b}")
            tensions.append(Tension(
                id=tid,
                claim_a=cid_a,
                claim_b=cid_b,
                description=(
                    f"Semantically similar (cos={sim:.2f}) but potentially contradictory:\n"
                    f"  A: {text_a[:100]}\n"
                    f"  B: {text_b[:100]}"
                ),
                domain=claim_a.get("domain", plugin_name),
                status="unresolved",
                first_seen=today,
            ))
            existing_pairs.add(pair)

    return tensions


# ---------------------------------------------------------------------------
# Combined detector
# ---------------------------------------------------------------------------

def detect_tensions(
    plugin_name: str,
    evidence: list[dict] | None = None,
    similarity_threshold: float = 0.75,
) -> list[Tension]:
    """Run all tension detection methods and return new tensions."""
    all_tensions = []

    if evidence:
        all_tensions.extend(detect_evidence_tensions(plugin_name, evidence))

    npz_file = knowledge_path(plugin_name) / "embeddings.npz"
    if npz_file.exists():
        all_tensions.extend(
            detect_semantic_tensions(plugin_name, similarity_threshold)
        )

    return all_tensions


def save_tensions(plugin_name: str, new_tensions: list[Tension]) -> int:
    """Append new tensions to tensions.jsonl. Returns count saved."""
    if not new_tensions:
        return 0

    kpath = knowledge_path(plugin_name)
    tensions_file = kpath / TENSIONS_FILE

    existing_ids: set[str] = set()
    if tensions_file.exists():
        for line in tensions_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_ids.add(json.loads(line).get("id", ""))

    saved = 0
    with open(tensions_file, "a", encoding="utf-8") as f:
        for tension in new_tensions:
            if tension.id not in existing_ids:
                f.write(tension.model_dump_json() + "\n")
                saved += 1

    return saved
