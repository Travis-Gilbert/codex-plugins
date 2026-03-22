"""Stage 2: Bayesian Confidence Updater.

Updates claim confidence using Beta distribution posterior updates and
temporal decay. This is pure math — no neural networks, no ML libraries.

Each claim's confidence is modeled as Beta(alpha, beta):
  - confidence = alpha / (alpha + beta)  (posterior mean)
  - uncertainty = 1 / (alpha + beta + 2)  (inversely proportional to evidence)

Update rules (from spec):
  - accepted:       alpha += 1.0
  - modified:       alpha += 0.5, beta += 0.3
  - rejected:       beta += 1.5  (rejections are stronger signal)
  - not_consulted:  beta += 0.1  (weak negative: not useful enough to surface)
  - consulted:      alpha += 0.2  (weak positive: was looked at)

Temporal decay:
  Every 30 days without validation, alpha *= 0.95, beta *= 0.95.
  This shrinks the distribution toward the prior — old unchallenged claims
  gradually lose certainty. Floor at 0.3 confidence from decay alone;
  only actual rejections can push below 0.3.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .config import (
    CLAIMS_FILE,
    CONFIDENCE_FLOOR,
    DECAY_FACTOR,
    DECAY_INTERVAL_DAYS,
    DEFAULT_ALPHA,
    DEFAULT_BETA,
    knowledge_path,
)


# ---------------------------------------------------------------------------
# Update deltas per outcome
# ---------------------------------------------------------------------------

OUTCOME_DELTAS: dict[str, tuple[float, float]] = {
    "accepted":       (1.0, 0.0),
    "modified":       (0.5, 0.3),
    "rejected":       (0.0, 1.5),
    "abandoned":      (0.0, 0.5),
    "consulted":      (0.2, 0.0),
    "not_consulted":  (0.0, 0.1),
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ConfidenceUpdate:
    """Track what changed for a single claim."""
    claim_id: str
    old_alpha: float
    old_beta: float
    new_alpha: float
    new_beta: float
    old_confidence: float
    new_confidence: float
    evidence_applied: int = 0
    decay_applied: bool = False

    @property
    def delta(self) -> float:
        return self.new_confidence - self.old_confidence


# ---------------------------------------------------------------------------
# Core updater
# ---------------------------------------------------------------------------

def compute_confidence(alpha: float, beta: float) -> float:
    """Posterior mean of Beta(alpha, beta)."""
    if alpha + beta == 0:
        return 0.5
    return alpha / (alpha + beta)


def apply_evidence(
    claims_data: list[dict],
    evidence: list[dict],
) -> tuple[list[dict], list[ConfidenceUpdate]]:
    """Apply evidence records to claims and return updated claims + change log.

    Args:
        claims_data: List of claim dicts (from claims.jsonl).
        evidence: List of evidence record dicts with claim_id and outcome.

    Returns:
        Tuple of (updated_claims, updates_applied).
    """
    # Index claims by ID
    claims_by_id: dict[str, dict] = {}
    for claim in claims_data:
        claims_by_id[claim["id"]] = claim

    # Aggregate evidence per claim
    evidence_by_claim: dict[str, list[str]] = defaultdict(list)
    for record in evidence:
        cid = record.get("claim_id", "")
        outcome = record.get("outcome", "")
        if cid and outcome:
            evidence_by_claim[cid].append(outcome)

    updates: list[ConfidenceUpdate] = []

    for cid, outcomes in evidence_by_claim.items():
        if cid not in claims_by_id:
            continue

        claim = claims_by_id[cid]

        # Only update active claims (draft claims don't get evidence updates)
        if claim.get("status") != "active":
            continue

        # Extract current alpha/beta from evidence counts
        # We track alpha/beta implicitly via the evidence field
        ev = claim.get("evidence", {"accepted": 0, "rejected": 0, "modified": 0})
        old_alpha = DEFAULT_ALPHA + ev.get("accepted", 0) + ev.get("modified", 0) * 0.5
        old_beta = DEFAULT_BETA + ev.get("rejected", 0) * 1.5 + ev.get("modified", 0) * 0.3
        old_confidence = compute_confidence(old_alpha, old_beta)

        new_alpha = old_alpha
        new_beta = old_beta
        evidence_count = 0

        for outcome in outcomes:
            d_alpha, d_beta = OUTCOME_DELTAS.get(outcome, (0.0, 0.0))
            new_alpha += d_alpha
            new_beta += d_beta
            evidence_count += 1

            # Update evidence counters on the claim
            if outcome == "accepted":
                ev["accepted"] = ev.get("accepted", 0) + 1
            elif outcome == "modified":
                ev["modified"] = ev.get("modified", 0) + 1
            elif outcome in ("rejected", "abandoned"):
                ev["rejected"] = ev.get("rejected", 0) + 1

        new_confidence = compute_confidence(new_alpha, new_beta)

        claim["evidence"] = ev
        claim["confidence"] = round(new_confidence, 4)
        claim["last_validated"] = date.today().isoformat()

        updates.append(ConfidenceUpdate(
            claim_id=cid,
            old_alpha=old_alpha,
            old_beta=old_beta,
            new_alpha=new_alpha,
            new_beta=new_beta,
            old_confidence=round(old_confidence, 4),
            new_confidence=round(new_confidence, 4),
            evidence_applied=evidence_count,
        ))

    return list(claims_by_id.values()), updates


def apply_temporal_decay(
    claims_data: list[dict],
    as_of: date | None = None,
) -> tuple[list[dict], list[ConfidenceUpdate]]:
    """Apply temporal decay to claims not validated recently.

    Every DECAY_INTERVAL_DAYS without validation, alpha and beta are
    multiplied by DECAY_FACTOR. This shrinks the distribution toward
    the prior. Confidence from decay alone cannot drop below CONFIDENCE_FLOOR.

    Args:
        claims_data: List of claim dicts.
        as_of: Reference date (defaults to today).

    Returns:
        Tuple of (updated_claims, decay_updates).
    """
    if as_of is None:
        as_of = date.today()

    updates: list[ConfidenceUpdate] = []

    for claim in claims_data:
        if claim.get("status") != "active":
            continue

        last_validated = claim.get("last_validated", "")
        if not last_validated:
            continue

        try:
            last_date = date.fromisoformat(last_validated)
        except ValueError:
            continue

        days_since = (as_of - last_date).days
        if days_since < DECAY_INTERVAL_DAYS:
            continue

        # Calculate number of decay periods
        periods = days_since // DECAY_INTERVAL_DAYS

        ev = claim.get("evidence", {"accepted": 0, "rejected": 0, "modified": 0})
        old_alpha = DEFAULT_ALPHA + ev.get("accepted", 0) + ev.get("modified", 0) * 0.5
        old_beta = DEFAULT_BETA + ev.get("rejected", 0) * 1.5 + ev.get("modified", 0) * 0.3
        old_confidence = compute_confidence(old_alpha, old_beta)

        # Apply decay
        decay = DECAY_FACTOR ** periods
        new_alpha = old_alpha * decay
        new_beta = old_beta * decay
        new_confidence = compute_confidence(new_alpha, new_beta)

        # Enforce floor: decay alone cannot push below CONFIDENCE_FLOOR
        # Only actual rejections can do that
        if new_confidence < CONFIDENCE_FLOOR and old_confidence >= CONFIDENCE_FLOOR:
            # Don't decay past the floor
            new_confidence = CONFIDENCE_FLOOR

        claim["confidence"] = round(new_confidence, 4)

        if abs(new_confidence - old_confidence) > 0.001:
            updates.append(ConfidenceUpdate(
                claim_id=claim["id"],
                old_alpha=old_alpha,
                old_beta=old_beta,
                new_alpha=new_alpha,
                new_beta=new_beta,
                old_confidence=round(old_confidence, 4),
                new_confidence=round(new_confidence, 4),
                decay_applied=True,
            ))

    return claims_data, updates


# ---------------------------------------------------------------------------
# File-level operations
# ---------------------------------------------------------------------------

def update_plugin_confidence(
    plugin_name: str,
    evidence: list[dict],
    apply_decay: bool = True,
) -> dict:
    """Full confidence update cycle for a plugin.

    1. Load claims.jsonl
    2. Apply evidence updates
    3. Apply temporal decay (optional)
    4. Write updated claims.jsonl
    5. Return summary stats

    Args:
        plugin_name: Plugin to update.
        evidence: Evidence records from evidence_collector.
        apply_decay: Whether to apply temporal decay.

    Returns:
        Summary dict with counts and notable changes.
    """
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE

    if not claims_file.exists():
        return {"error": f"No claims file found for {plugin_name}"}

    # Load claims
    claims_data = []
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            claims_data.append(json.loads(line))

    # Apply evidence
    claims_data, evidence_updates = apply_evidence(claims_data, evidence)

    # Apply decay
    decay_updates: list[ConfidenceUpdate] = []
    if apply_decay:
        claims_data, decay_updates = apply_temporal_decay(claims_data)

    # Write back
    with open(claims_file, "w", encoding="utf-8") as f:
        for claim in claims_data:
            f.write(json.dumps(claim, ensure_ascii=False) + "\n")

    # Compute summary
    active_claims = [c for c in claims_data if c.get("status") == "active"]
    avg_confidence = (
        sum(c.get("confidence", 0) for c in active_claims) / len(active_claims)
        if active_claims else 0
    )

    # Flag claims that dropped below 0.5 (may need review)
    flagged = [
        u for u in evidence_updates
        if u.new_confidence < 0.5 and u.old_confidence >= 0.5
    ]

    # Flag claims that rose above 0.8 (high confidence)
    promoted = [
        u for u in evidence_updates
        if u.new_confidence >= 0.8 and u.old_confidence < 0.8
    ]

    return {
        "plugin": plugin_name,
        "evidence_records": len(evidence),
        "claims_updated": len(evidence_updates),
        "claims_decayed": len(decay_updates),
        "avg_confidence": round(avg_confidence, 4),
        "flagged_low": [
            {"claim_id": u.claim_id, "confidence": u.new_confidence, "delta": round(u.delta, 4)}
            for u in flagged
        ],
        "promoted_high": [
            {"claim_id": u.claim_id, "confidence": u.new_confidence, "delta": round(u.delta, 4)}
            for u in promoted
        ],
    }
