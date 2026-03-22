---
description: Run the between-session learning pipeline — collect evidence from session logs, update claim confidence via Bayesian updates, apply temporal decay
allowed-tools: Read, Bash
argument-hint: "[--dry-run]  (preview changes without writing)"
---

# Knowledge Update

Run the epistemic learning pipeline to update claim confidence from accumulated session evidence.

## What It Does

1. **Evidence Collection** (Stage 1) — Reads `knowledge/session_log/*.jsonl` for unprocessed sessions. Classifies outcomes per claim: accepted, modified, rejected, abandoned, consulted, not_consulted.

2. **Confidence Updates** (Stage 2) — Applies Bayesian Beta distribution updates to each active claim:
   - Accepted suggestion: alpha += 1.0 (claim strengthened)
   - Modified suggestion: alpha += 0.5, beta += 0.3 (partial validation)
   - Rejected suggestion: beta += 1.5 (strong negative signal)
   - Not consulted: beta += 0.1 (weak negative: wasn't useful enough to surface)
   - Consulted: alpha += 0.2 (weak positive: was referenced)

3. **Temporal Decay** — Claims not validated in 30+ days get alpha and beta multiplied by 0.95 per period. This moves stale claims toward uncertainty. Confidence floor at 0.3 from decay alone.

4. **Manifest Update** — Recalculates stats (total, active, draft counts, avg confidence) and logs the pipeline run.

## How to Run

### From Claude Code

Run this command directly. It will execute the pipeline and report results.

### From the terminal

```bash
cd /path/to/codex-plugins

# Run for a specific plugin
python3 -m scripts.epistemic.run_pipeline django-design

# Preview without writing changes
python3 -m scripts.epistemic.run_pipeline django-design --dry-run

# Run for all plugins
python3 -m scripts.epistemic.run_pipeline --all

# Run only specific stages
python3 -m scripts.epistemic.run_pipeline django-design --stages 1,2
```

## Steps (for Claude Code execution)

1. Run the pipeline:
```bash
cd <repo-root> && python3 -m scripts.epistemic.run_pipeline <plugin-name>
```

2. Report the output:
   - How many evidence records were collected
   - How many claims were updated
   - How many claims decayed
   - Average confidence of active claims
   - Any claims that dropped below 0.5 (may need review)
   - Any claims that rose above 0.8 (newly high-confidence)

3. If claims dropped below 0.5, suggest running `/knowledge-review` to inspect them.

## Future Stages (Sprint 4-5)

The pipeline will grow to include:
- [3] Pattern Extractor — SBERT + HDBSCAN clustering of code changes
- [4] Tension Detector — contradiction finder
- [5] Relevance Scorer — MLP training
- [6] Embedding Update — SBERT re-embedding
- [7] Question Generator — flag low-confidence claims
- [8] Cross-Plugin Linker — semantic neighbor search across plugins
