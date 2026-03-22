"""Stage 7: Question Generator.

Automatically generates Question records from signals in the knowledge base:

1. Low-confidence claims (below threshold) — "Is this still valid?"
2. Long-unresolved tensions — "How should this conflict be resolved?"
3. Methods with low success rates — "Is this method still the right approach?"
4. Claims with high evidence volume but middling confidence — "Needs more clarity"

All generated questions start at status "open" and require human triage
via /knowledge-review.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .config import (
    CLAIMS_FILE,
    METHODS_FILE,
    QUESTIONS_FILE,
    TENSIONS_FILE,
    knowledge_path,
)
from .schema import Question, claim_id as make_id


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

LOW_CONFIDENCE_THRESHOLD = 0.45
HIGH_EVIDENCE_MIN = 5  # total evidence events
MIDDLING_CONFIDENCE_RANGE = (0.4, 0.65)
TENSION_AGE_DAYS = 30  # flag tensions older than this


# ---------------------------------------------------------------------------
# Question generators
# ---------------------------------------------------------------------------

def questions_from_low_confidence(plugin_name: str) -> list[Question]:
    """Flag active claims with low confidence as questions."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    if not claims_file.exists():
        return []

    questions = []
    today = date.today().isoformat()

    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        claim = json.loads(line)

        if claim.get("status") != "active":
            continue
        if claim.get("confidence", 1.0) >= LOW_CONFIDENCE_THRESHOLD:
            continue

        qid = make_id(plugin_name, f"q-low-conf-{claim['id']}")
        questions.append(Question(
            id=qid,
            text=(
                f"Low confidence ({claim['confidence']:.2f}): "
                f"'{claim['text'][:80]}...' — Is this claim still valid? "
                f"Should it be retired or refined?"
            ),
            domain=claim.get("domain", plugin_name),
            raised_by="question_generator",
            raised_date=today,
            related_claims=[claim["id"]],
            priority="high" if claim["confidence"] < 0.3 else "medium",
        ))

    return questions


def questions_from_stale_tensions(plugin_name: str) -> list[Question]:
    """Flag long-unresolved tensions as questions."""
    kpath = knowledge_path(plugin_name)
    tensions_file = kpath / TENSIONS_FILE
    if not tensions_file.exists():
        return []

    questions = []
    today = date.today()
    today_iso = today.isoformat()

    for line in tensions_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        tension = json.loads(line)

        if tension.get("status") != "unresolved":
            continue

        first_seen = tension.get("first_seen", "")
        if not first_seen:
            continue

        try:
            age_days = (today - date.fromisoformat(first_seen)).days
        except ValueError:
            continue

        if age_days < TENSION_AGE_DAYS:
            continue

        qid = make_id(plugin_name, f"q-stale-tension-{tension['id']}")
        questions.append(Question(
            id=qid,
            text=(
                f"Unresolved tension ({age_days} days): "
                f"{tension.get('description', '')[:100]}... — "
                f"Can this be resolved or classified as context-dependent?"
            ),
            domain=tension.get("domain", plugin_name),
            raised_by="question_generator",
            raised_date=today_iso,
            related_tensions=[tension["id"]],
            related_claims=[tension.get("claim_a", ""), tension.get("claim_b", "")],
            priority="medium",
        ))

    return questions


def questions_from_high_evidence_middling_confidence(plugin_name: str) -> list[Question]:
    """Flag claims with lots of evidence but still-uncertain confidence."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    if not claims_file.exists():
        return []

    questions = []
    today = date.today().isoformat()

    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        claim = json.loads(line)

        if claim.get("status") != "active":
            continue

        ev = claim.get("evidence", {})
        total_evidence = ev.get("accepted", 0) + ev.get("rejected", 0) + ev.get("modified", 0)
        conf = claim.get("confidence", 0.667)

        if total_evidence < HIGH_EVIDENCE_MIN:
            continue
        if not (MIDDLING_CONFIDENCE_RANGE[0] <= conf <= MIDDLING_CONFIDENCE_RANGE[1]):
            continue

        qid = make_id(plugin_name, f"q-middling-{claim['id']}")
        questions.append(Question(
            id=qid,
            text=(
                f"High evidence ({total_evidence} events) but uncertain "
                f"confidence ({conf:.2f}): '{claim['text'][:80]}...' — "
                f"This claim is contested. Should it be split into "
                f"context-dependent variants?"
            ),
            domain=claim.get("domain", plugin_name),
            raised_by="question_generator",
            raised_date=today,
            related_claims=[claim["id"]],
            priority="high",
        ))

    return questions


# ---------------------------------------------------------------------------
# Combined generator
# ---------------------------------------------------------------------------

def generate_questions(plugin_name: str) -> list[Question]:
    """Run all question generators and return new questions."""
    all_questions = []
    all_questions.extend(questions_from_low_confidence(plugin_name))
    all_questions.extend(questions_from_stale_tensions(plugin_name))
    all_questions.extend(questions_from_high_evidence_middling_confidence(plugin_name))
    return all_questions


def save_questions(plugin_name: str, new_questions: list[Question]) -> int:
    """Append new questions to questions.jsonl. Returns count saved."""
    if not new_questions:
        return 0

    kpath = knowledge_path(plugin_name)
    questions_file = kpath / QUESTIONS_FILE

    existing_ids: set[str] = set()
    if questions_file.exists():
        for line in questions_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing_ids.add(json.loads(line).get("id", ""))

    saved = 0
    with open(questions_file, "a", encoding="utf-8") as f:
        for q in new_questions:
            if q.id not in existing_ids:
                f.write(q.model_dump_json() + "\n")
                saved += 1

    return saved
