"""Fast epistemic learning for /learn command invocation.

Runs the lightweight learning stages (evidence, confidence, tensions,
questions) and produces a review queue. Does NOT run heavy ML stages
(SBERT, HDBSCAN, MLP). Those remain in run_pipeline.py --deep.

Usage:
    python -m scripts.epistemic.learn --plugin next-pro
    python -m scripts.epistemic.learn --plugin next-pro --session path/to/log.jsonl
    python -m scripts.epistemic.learn --all

Output:
    Writes knowledge/.review_queue.json with items for the /learn
    command to present to the user. Prints a summary to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from .config import (
    MANIFEST_FILE,
    PLUGINS,
    TENSIONS_FILE,
    QUESTIONS_FILE,
    knowledge_path,
    plugin_path,
)


# ---------------------------------------------------------------------------
# Core learning stages (import from existing scripts)
# ---------------------------------------------------------------------------

def _collect_evidence(plugin_name: str) -> list[dict]:
    """Stage 1: Collect evidence from unprocessed session logs + git diffs."""
    try:
        from .evidence_collector import collect_evidence
        return collect_evidence(plugin_name)
    except Exception as e:
        print(f"  Evidence collection skipped: {e}", file=sys.stderr)
        return []


def _update_confidence(plugin_name: str, evidence: list[dict]) -> dict:
    """Stage 2: Bayesian confidence updates + temporal decay."""
    try:
        from .confidence_updater import update_plugin_confidence
        return update_plugin_confidence(plugin_name, evidence, apply_decay=True)
    except Exception as e:
        print(f"  Confidence update skipped: {e}", file=sys.stderr)
        return {}


def _detect_tensions(plugin_name: str, evidence: list[dict]) -> list[dict]:
    """Stage 4: Find contradictory outcomes across claims."""
    try:
        from .tension_detector import detect_tensions, save_tensions
        tensions = detect_tensions(plugin_name, evidence=evidence)
        if tensions:
            save_tensions(plugin_name, tensions)
        return [{"description": t.description, "claims": t.related_claims}
                for t in tensions] if tensions else []
    except Exception as e:
        print(f"  Tension detection skipped: {e}", file=sys.stderr)
        return []


def _flag_questions(plugin_name: str) -> list[dict]:
    """Stage 7: Flag low-confidence and stale claims."""
    try:
        from .question_generator import generate_questions, save_questions
        questions = generate_questions(plugin_name)
        if questions:
            save_questions(plugin_name, questions)
        return [{"claim_id": q.claim_id, "text": q.text, "priority": q.priority,
                 "reason": q.reason}
                for q in questions] if questions else []
    except Exception as e:
        print(f"  Question flagging skipped: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Candidate claim extraction from latest session
# ---------------------------------------------------------------------------

def _extract_candidates(plugin_name: str, session_file: Path | None = None) -> list[dict]:
    """Extract candidate claims logged during the session."""
    from .session_logger import list_session_logs, read_session_log

    if session_file:
        logs = [session_file]
    else:
        logs = list_session_logs(plugin_name)
        if not logs:
            return []
        logs = [logs[0]]  # Only the most recent session

    candidates = []
    for log_path in logs:
        events = read_session_log(log_path)
        for event in events:
            if event.get("event") == "candidate_claim":
                candidates.append({
                    "text": event.get("description", ""),
                    "source": "session_observation",
                    "related_claims": event.get("related_claims", []),
                })
    return candidates


# ---------------------------------------------------------------------------
# Read current claim stats
# ---------------------------------------------------------------------------

def _read_claim_stats(plugin_name: str) -> dict:
    """Read current claim counts and average confidence."""
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / "claims.jsonl"

    if not claims_file.exists():
        return {"total": 0, "active": 0, "draft": 0, "avg_confidence": 0.0}

    claims = []
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            claims.append(json.loads(line))

    active = [c for c in claims if c.get("status") == "active"]
    draft = [c for c in claims if c.get("status") == "draft"]

    avg_conf = (
        round(sum(c.get("confidence", 0) for c in active) / len(active), 3)
        if active else 0.0
    )

    return {
        "total": len(claims),
        "active": len(active),
        "draft": len(draft),
        "avg_confidence": avg_conf,
    }


# ---------------------------------------------------------------------------
# Review queue builder
# ---------------------------------------------------------------------------

def build_review_queue(
    plugin_name: str,
    confidence_result: dict,
    tensions: list[dict],
    questions: list[dict],
    candidates: list[dict],
    claim_stats: dict,
    evidence_count: int,
) -> dict:
    """Build the .review_queue.json for the /learn command to present."""

    # Extract confidence changes from the updater result
    confidence_changes = []

    for item in confidence_result.get("flagged_low", []):
        confidence_changes.append({
            "claim_id": item["claim_id"],
            "old": round(item.get("old_confidence", 0), 3),
            "new": round(item["confidence"], 3),
            "reason": "weakened",
        })

    for item in confidence_result.get("promoted_high", []):
        confidence_changes.append({
            "claim_id": item["claim_id"],
            "old": round(item.get("old_confidence", 0), 3),
            "new": round(item["confidence"], 3),
            "reason": "strengthened",
        })

    # Build attention-needed list from questions
    attention = []
    for q in questions:
        attention.append({
            "claim_id": q.get("claim_id", ""),
            "confidence": 0,  # Will be filled from claims if needed
            "reason": q.get("reason", "flagged"),
            "text": q.get("text", ""),
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "plugin": plugin_name,
        "confidence_changes": confidence_changes,
        "new_tensions": tensions,
        "candidate_claims": candidates,
        "attention_needed": attention,
        "summary": {
            "total_claims": claim_stats["total"],
            "active_claims": claim_stats["active"],
            "avg_confidence": claim_stats["avg_confidence"],
            "evidence_records": evidence_count,
            "claims_updated": confidence_result.get("claims_updated", 0),
            "new_tensions": len(tensions),
            "candidates": len(candidates),
        },
    }


# ---------------------------------------------------------------------------
# Manifest update
# ---------------------------------------------------------------------------

def _update_manifest(plugin_name: str, summary: dict) -> None:
    """Update manifest.json after learning."""
    kpath = knowledge_path(plugin_name)
    manifest_file = kpath / MANIFEST_FILE

    if not manifest_file.exists():
        return

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    # Update stats from current claims
    stats = _read_claim_stats(plugin_name)
    manifest["stats"]["total_claims"] = stats["total"]
    manifest["stats"]["active_claims"] = stats["active"]
    manifest["stats"]["draft_claims"] = stats["draft"]
    manifest["stats"]["avg_confidence"] = stats["avg_confidence"]

    manifest["last_updated"] = date.today().isoformat()

    # Add log entry
    log_entry = {
        "date": datetime.now().isoformat(),
        "action": "learn",
        "details": (
            f"Evidence: {summary.get('evidence_records', 0)}, "
            f"Updated: {summary.get('claims_updated', 0)}, "
            f"Tensions: {summary.get('new_tensions', 0)}, "
            f"Candidates: {summary.get('candidates', 0)}"
        ),
    }
    manifest.setdefault("update_log", []).append(log_entry)
    manifest["update_log"] = manifest["update_log"][-50:]

    manifest_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def learn(
    plugin_name: str,
    session_file: Path | None = None,
) -> dict:
    """Run the fast learning pipeline for a plugin.

    Returns the review queue dict (also written to .review_queue.json).
    """
    kpath = knowledge_path(plugin_name)

    print(f"\n{'='*50}", file=sys.stderr)
    print(f"/learn: {plugin_name}", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)

    # 1. Evidence collection
    print(f"  Collecting evidence...", file=sys.stderr)
    evidence = _collect_evidence(plugin_name)
    print(f"    {len(evidence)} evidence records", file=sys.stderr)

    # 2. Confidence updates
    print(f"  Updating confidence...", file=sys.stderr)
    confidence_result = _update_confidence(plugin_name, evidence)
    updated = confidence_result.get("claims_updated", 0)
    decayed = confidence_result.get("claims_decayed", 0)
    print(f"    {updated} updated, {decayed} decayed", file=sys.stderr)

    # 3. Tension detection
    print(f"  Checking for tensions...", file=sys.stderr)
    tensions = _detect_tensions(plugin_name, evidence)
    print(f"    {len(tensions)} new tensions", file=sys.stderr)

    # 4. Question flagging
    print(f"  Flagging questions...", file=sys.stderr)
    questions = _flag_questions(plugin_name)
    print(f"    {len(questions)} items flagged", file=sys.stderr)

    # 5. Extract candidate claims from session
    print(f"  Extracting candidates...", file=sys.stderr)
    candidates = _extract_candidates(plugin_name, session_file)
    print(f"    {len(candidates)} candidates", file=sys.stderr)

    # 6. Read current stats
    claim_stats = _read_claim_stats(plugin_name)

    # 7. Build review queue
    review_queue = build_review_queue(
        plugin_name=plugin_name,
        confidence_result=confidence_result,
        tensions=tensions,
        questions=questions,
        candidates=candidates,
        claim_stats=claim_stats,
        evidence_count=len(evidence),
    )

    # 8. Write review queue
    queue_file = kpath / ".review_queue.json"
    queue_file.write_text(
        json.dumps(review_queue, indent=2, ensure_ascii=False) + "\n"
    )

    # 9. Update manifest
    _update_manifest(plugin_name, review_queue["summary"])

    # 10. Print summary to stdout (for /learn command to read)
    summary = review_queue["summary"]
    print(f"\n{plugin_name}: {summary['active_claims']} active claims, "
          f"avg confidence {summary['avg_confidence']:.2f}", file=sys.stderr)

    # Print review items count
    review_items = (
        len(review_queue["confidence_changes"])
        + len(review_queue["new_tensions"])
        + len(review_queue["candidate_claims"])
        + len(review_queue["attention_needed"])
    )
    if review_items:
        print(f"  {review_items} items for review", file=sys.stderr)

    # Write summary as JSON to stdout for the /learn command to parse
    print(json.dumps(review_queue, indent=2))

    return review_queue


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fast epistemic learning (runs on /learn)",
    )
    parser.add_argument(
        "plugin",
        nargs="?",
        choices=list(PLUGINS.keys()),
        help="Plugin to learn for",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Learn for all registered plugins",
    )
    parser.add_argument(
        "--session",
        type=str,
        default=None,
        help="Path to specific session log file",
    )

    args = parser.parse_args()

    if args.all:
        for name in PLUGINS:
            ppath = plugin_path(name)
            if ppath.exists() and (knowledge_path(name)).exists():
                learn(name)
    elif args.plugin:
        session = Path(args.session) if args.session else None
        learn(args.plugin, session_file=session)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
