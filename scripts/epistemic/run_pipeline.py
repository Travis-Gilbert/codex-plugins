"""Pipeline orchestrator — runs epistemic learning stages in sequence.

Usage:
    python -m scripts.epistemic.run_pipeline django-design
    python -m scripts.epistemic.run_pipeline --all
    python -m scripts.epistemic.run_pipeline django-design --stages 1,2
    python -m scripts.epistemic.run_pipeline django-design --dry-run

Stages:
  [1] Evidence Collector — session logs -> evidence records
  [2] Confidence Updater — Bayesian updates + temporal decay
  [3] Pattern Extractor — SBERT + HDBSCAN clustering
  [4] Tension Detector — contradiction finder
  [5] Relevance Scorer — MLP training (Sprint 5)
  [6] Embedding Update — SBERT re-embedding
  [7] Question Generator — flag low-confidence claims
  [8] Cross-Plugin Linker — semantic neighbor search (Sprint 5)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .config import MANIFEST_FILE, PLUGINS, TENSIONS_FILE, QUESTIONS_FILE, knowledge_path, plugin_path
from .evidence_collector import collect_evidence
from .confidence_updater import update_plugin_confidence
from .schema import UpdateLogEntry


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def stage_1_evidence(plugin_name: str, dry_run: bool = False) -> list[dict]:
    """Stage 1: Collect evidence from session logs."""
    print(f"  [1] Evidence Collector: {plugin_name}", file=sys.stderr)

    evidence = collect_evidence(plugin_name)

    if not evidence:
        print(f"      No new evidence found", file=sys.stderr)
        return []

    # Summarize evidence
    from collections import Counter
    outcomes = Counter(e["outcome"] for e in evidence)
    print(f"      Found {len(evidence)} evidence records:", file=sys.stderr)
    for outcome, count in outcomes.most_common():
        print(f"        {outcome}: {count}", file=sys.stderr)

    if dry_run:
        for e in evidence:
            print(json.dumps(e))
        return evidence

    return evidence


def stage_2_confidence(
    plugin_name: str,
    evidence: list[dict],
    dry_run: bool = False,
) -> dict:
    """Stage 2: Update claim confidence from evidence."""
    print(f"  [2] Confidence Updater: {plugin_name}", file=sys.stderr)

    if not evidence:
        print(f"      No evidence to apply, checking temporal decay only", file=sys.stderr)

    if dry_run:
        print(f"      Dry run — no changes written", file=sys.stderr)
        return {"plugin": plugin_name, "dry_run": True}

    result = update_plugin_confidence(plugin_name, evidence, apply_decay=True)

    print(f"      Claims updated: {result.get('claims_updated', 0)}", file=sys.stderr)
    print(f"      Claims decayed: {result.get('claims_decayed', 0)}", file=sys.stderr)
    print(f"      Avg confidence: {result.get('avg_confidence', 0):.3f}", file=sys.stderr)

    if result.get("flagged_low"):
        print(f"      ⚠ Claims dropped below 0.5:", file=sys.stderr)
        for f in result["flagged_low"]:
            print(f"        {f['claim_id']}: {f['confidence']:.3f} (Δ{f['delta']:+.3f})", file=sys.stderr)

    if result.get("promoted_high"):
        print(f"      ★ Claims promoted above 0.8:", file=sys.stderr)
        for p in result["promoted_high"]:
            print(f"        {p['claim_id']}: {p['confidence']:.3f} (Δ{p['delta']:+.3f})", file=sys.stderr)

    return result


def stage_3_patterns(plugin_name: str, dry_run: bool = False) -> int:
    """Stage 3: Discover patterns from session suggestion clustering."""
    print(f"  [3] Pattern Extractor: {plugin_name}", file=sys.stderr)

    from .pattern_extractor import extract_patterns, save_pattern_claims

    patterns = extract_patterns(plugin_name)
    if not patterns:
        print(f"      No new patterns discovered", file=sys.stderr)
        return 0

    print(f"      Proposed {len(patterns)} new claims from patterns", file=sys.stderr)
    if dry_run:
        for p in patterns:
            print(f"        {p.text[:80]}", file=sys.stderr)
        return len(patterns)

    saved = save_pattern_claims(plugin_name, patterns)
    print(f"      Saved {saved} new pattern-based claims (draft)", file=sys.stderr)
    return saved


def stage_4_tensions(
    plugin_name: str,
    evidence: list[dict],
    dry_run: bool = False,
) -> int:
    """Stage 4: Detect tensions between claims."""
    print(f"  [4] Tension Detector: {plugin_name}", file=sys.stderr)

    from .tension_detector import detect_tensions, save_tensions

    tensions = detect_tensions(plugin_name, evidence=evidence)
    if not tensions:
        print(f"      No new tensions detected", file=sys.stderr)
        return 0

    print(f"      Found {len(tensions)} new tensions", file=sys.stderr)
    for t in tensions:
        print(f"        {t.description[:80]}...", file=sys.stderr)

    if dry_run:
        return len(tensions)

    saved = save_tensions(plugin_name, tensions)
    print(f"      Saved {saved} tensions", file=sys.stderr)
    return saved


def stage_5_scorer(plugin_name: str, dry_run: bool = False) -> dict:
    """Stage 5: Train the relevance scorer MLP."""
    print(f"  [5] Relevance Scorer: {plugin_name}", file=sys.stderr)

    if dry_run:
        print(f"      Dry run — no training", file=sys.stderr)
        return {}

    from .relevance_scorer import train_scorer
    result = train_scorer(plugin_name)
    status = result.get("status", "unknown")

    if status == "trained":
        print(f"      Trained! Accuracy: {result['accuracy']:.3f}", file=sys.stderr)
    elif status == "skipped":
        print(f"      Skipped: {result.get('reason', '')}", file=sys.stderr)
    else:
        print(f"      Error: {result.get('reason', '')}", file=sys.stderr)

    return result


def stage_8_cross_links(dry_run: bool = False) -> dict:
    """Stage 8: Cross-plugin semantic linking."""
    print(f"  [8] Cross-Plugin Linker", file=sys.stderr)

    if dry_run:
        print(f"      Dry run — no links created", file=sys.stderr)
        return {}

    from .cross_linker import link_plugins
    return link_plugins()


def stage_6_embeddings(plugin_name: str, dry_run: bool = False) -> dict:
    """Stage 6: Generate/update SBERT embeddings for all claims."""
    print(f"  [6] Embedding Update: {plugin_name}", file=sys.stderr)

    if dry_run:
        print(f"      Dry run — no embeddings generated", file=sys.stderr)
        return {}

    from .embedding_manager import embed_plugin
    result = embed_plugin(plugin_name)
    embedded = result.get("embedded", 0)
    total = result.get("total", 0)
    print(f"      Embedded {embedded} new claims ({total} total)", file=sys.stderr)
    return result


def stage_7_questions(plugin_name: str, dry_run: bool = False) -> int:
    """Stage 7: Generate questions from low-confidence signals."""
    print(f"  [7] Question Generator: {plugin_name}", file=sys.stderr)

    from .question_generator import generate_questions, save_questions

    questions = generate_questions(plugin_name)
    if not questions:
        print(f"      No new questions generated", file=sys.stderr)
        return 0

    print(f"      Generated {len(questions)} questions", file=sys.stderr)
    for q in questions:
        print(f"        [{q.priority}] {q.text[:70]}...", file=sys.stderr)

    if dry_run:
        return len(questions)

    saved = save_questions(plugin_name, questions)
    print(f"      Saved {saved} questions", file=sys.stderr)
    return saved


# ---------------------------------------------------------------------------
# Manifest update
# ---------------------------------------------------------------------------

def update_manifest(plugin_name: str, pipeline_result: dict) -> None:
    """Update the plugin's manifest.json after a pipeline run."""
    kpath = knowledge_path(plugin_name)
    manifest_file = kpath / MANIFEST_FILE

    if not manifest_file.exists():
        return

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    # Recount claims from the actual file
    claims_file = kpath / "claims.jsonl"
    if claims_file.exists():
        claims = []
        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                claims.append(json.loads(line))

        active = [c for c in claims if c.get("status") == "active"]
        draft = [c for c in claims if c.get("status") == "draft"]

        manifest["stats"]["total_claims"] = len(claims)
        manifest["stats"]["active_claims"] = len(active)
        manifest["stats"]["draft_claims"] = len(draft)
        manifest["stats"]["avg_confidence"] = (
            round(sum(c.get("confidence", 0) for c in active) / len(active), 4)
            if active else 0
        )

    # Recount tensions
    tensions_file = kpath / TENSIONS_FILE
    if tensions_file.exists():
        tension_count = sum(1 for l in tensions_file.read_text().splitlines() if l.strip())
        manifest["stats"]["tensions"] = tension_count

    # Recount questions
    questions_file = kpath / QUESTIONS_FILE
    if questions_file.exists():
        question_count = sum(1 for l in questions_file.read_text().splitlines() if l.strip())
        manifest["stats"]["questions"] = question_count

    manifest["last_updated"] = date.today().isoformat()

    # Add update log entry
    log_entry = {
        "date": date.today().isoformat(),
        "action": "pipeline_run",
        "details": (
            f"Evidence: {pipeline_result.get('evidence_records', 0)}, "
            f"Updated: {pipeline_result.get('claims_updated', 0)}, "
            f"Decayed: {pipeline_result.get('claims_decayed', 0)}, "
            f"Tensions: {pipeline_result.get('tensions', 0)}, "
            f"Questions: {pipeline_result.get('questions', 0)}"
        ),
    }
    manifest.setdefault("update_log", []).append(log_entry)

    # Keep only last 50 log entries
    manifest["update_log"] = manifest["update_log"][-50:]

    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(
    plugin_name: str,
    stages: list[int] | None = None,
    dry_run: bool = False,
) -> dict:
    """Run the epistemic learning pipeline for a plugin.

    Args:
        plugin_name: Plugin to process.
        stages: List of stage numbers to run (default: all available).
        dry_run: If True, print results without writing changes.

    Returns:
        Pipeline result dict.
    """
    if stages is None:
        stages = [1, 2, 3, 4, 5, 6, 7, 8]

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Epistemic Pipeline: {plugin_name}", file=sys.stderr)
    print(f"Stages: {stages}", file=sys.stderr)
    if dry_run:
        print(f"Mode: DRY RUN", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    result = {"plugin": plugin_name, "stages_run": stages}
    evidence: list[dict] = []

    if 1 in stages:
        evidence = stage_1_evidence(plugin_name, dry_run=dry_run)
        result["evidence_records"] = len(evidence)

    if 2 in stages:
        confidence_result = stage_2_confidence(plugin_name, evidence, dry_run=dry_run)
        result["confidence"] = confidence_result
        result["claims_updated"] = confidence_result.get("claims_updated", 0)
        result["claims_decayed"] = confidence_result.get("claims_decayed", 0)

    if 3 in stages:
        result["patterns"] = stage_3_patterns(plugin_name, dry_run=dry_run)

    if 4 in stages:
        result["tensions"] = stage_4_tensions(plugin_name, evidence, dry_run=dry_run)

    if 5 in stages:
        result["scorer"] = stage_5_scorer(plugin_name, dry_run=dry_run)

    if 6 in stages:
        result["embeddings"] = stage_6_embeddings(plugin_name, dry_run=dry_run)

    if 7 in stages:
        result["questions"] = stage_7_questions(plugin_name, dry_run=dry_run)

    if 8 in stages:
        result["cross_links"] = stage_8_cross_links(dry_run=dry_run)

    if not dry_run:
        update_manifest(plugin_name, result)

    print(f"\nPipeline complete for {plugin_name}.", file=sys.stderr)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the epistemic learning pipeline",
    )
    parser.add_argument(
        "plugin",
        nargs="?",
        choices=list(PLUGINS.keys()),
        help="Plugin to process (omit with --all for everything)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run pipeline for all plugins",
    )
    parser.add_argument(
        "--stages",
        type=str,
        default="1,2,3,4,5,6,7,8",
        help="Comma-separated stage numbers to run (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print results without writing changes",
    )

    args = parser.parse_args()
    stages = [int(s.strip()) for s in args.stages.split(",")]

    if args.all:
        for name in PLUGINS:
            ppath = plugin_path(name)
            if ppath.exists():
                run_pipeline(name, stages=stages, dry_run=args.dry_run)
    elif args.plugin:
        run_pipeline(args.plugin, stages=stages, dry_run=args.dry_run)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
