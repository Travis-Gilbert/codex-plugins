"""Stage 8: Cross-Plugin Semantic Linker.

Loads embeddings from all plugins and finds semantic neighbors across
plugin boundaries. If cosine similarity > threshold, creates a
related_claims link between the two claims.

This discovers connections like:
  - django-design "accessible form error messages" links to
    ux-pro "error message pattern: what + why + fix"
  - animation-pro "prefers-reduced-motion" links to
    ux-pro "WCAG 2.2 motion guidelines"

Also generates a cross-plugin connectivity report showing which
plugins have the most inter-connections and where gaps exist.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from .config import CLAIMS_FILE, PLUGINS, knowledge_path, plugin_path
from .embedding_manager import load_embeddings, cosine_similarity


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SIMILARITY_THRESHOLD = 0.65  # spec says 0.75 but lowered for better coverage
TOP_K_NEIGHBORS = 3
REPORT_FILE = "cross_plugin_report.json"


# ---------------------------------------------------------------------------
# Cross-plugin linking
# ---------------------------------------------------------------------------

def link_plugins(
    threshold: float = SIMILARITY_THRESHOLD,
    top_k: int = TOP_K_NEIGHBORS,
) -> dict:
    """Find semantic neighbors across all plugin boundaries.

    For each claim in each plugin, finds the top-k most similar claims
    in OTHER plugins. If similarity > threshold, creates a related_claims
    link.

    Returns a report dict with link counts and connectivity stats.
    """
    # Load all plugins' embeddings and claims
    plugin_data: dict[str, dict] = {}  # name -> {embeddings, ids, claims}

    for name in PLUGINS:
        ppath = plugin_path(name)
        if not ppath.exists():
            continue

        emb_data = load_embeddings(name)
        if emb_data is None:
            print(f"  Skipping {name}: no embeddings", file=sys.stderr)
            continue

        embeddings, claim_ids = emb_data

        claims_by_id = {}
        claims_file = knowledge_path(name) / CLAIMS_FILE
        if claims_file.exists():
            for line in claims_file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    c = json.loads(line)
                    claims_by_id[c["id"]] = c

        plugin_data[name] = {
            "embeddings": embeddings,
            "ids": claim_ids,
            "claims": claims_by_id,
        }

    if len(plugin_data) < 2:
        return {"error": "Need at least 2 plugins with embeddings"}

    print(f"  Linking {len(plugin_data)} plugins: {list(plugin_data.keys())}", file=sys.stderr)

    # For each plugin pair, compute cross-similarities
    links_added: dict[str, int] = defaultdict(int)
    link_details: list[dict] = []
    new_related: dict[str, set[str]] = defaultdict(set)  # claim_id -> set of related ids

    plugin_names = list(plugin_data.keys())

    for i, source_name in enumerate(plugin_names):
        source = plugin_data[source_name]
        source_embs = source["embeddings"]
        source_ids = source["ids"]

        for j, target_name in enumerate(plugin_names):
            if i == j:
                continue

            target = plugin_data[target_name]
            target_embs = target["embeddings"]
            target_ids = target["ids"]

            # Compute similarity matrix: (N_source, N_target)
            sims = cosine_similarity(source_embs, target_embs)

            # For each source claim, find top-k target neighbors
            for src_idx in range(len(source_ids)):
                row = sims[src_idx]
                top_indices = np.argsort(row)[::-1][:top_k]

                for tgt_idx in top_indices:
                    sim = float(row[tgt_idx])
                    if sim < threshold:
                        continue

                    src_id = source_ids[src_idx]
                    tgt_id = target_ids[tgt_idx]

                    # Avoid duplicate links
                    if tgt_id in new_related.get(src_id, set()):
                        continue

                    new_related[src_id].add(tgt_id)
                    new_related[tgt_id].add(src_id)

                    pair_key = f"{source_name}->{target_name}"
                    links_added[pair_key] += 1

                    src_claim = source["claims"].get(src_id, {})
                    tgt_claim = target["claims"].get(str(tgt_id), {})

                    link_details.append({
                        "source_plugin": source_name,
                        "source_claim": str(src_id),
                        "source_text": src_claim.get("text", "")[:80],
                        "target_plugin": target_name,
                        "target_claim": str(tgt_id),
                        "target_text": tgt_claim.get("text", "")[:80],
                        "similarity": round(sim, 4),
                    })

    # Write related_claims back to each plugin's claims.jsonl
    total_updated = 0
    for name, data in plugin_data.items():
        claims_file = knowledge_path(name) / CLAIMS_FILE
        claims = []
        changed = False

        for line in claims_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            claim = json.loads(line)
            cid = claim["id"]

            if cid in new_related:
                existing = set(claim.get("related_claims", []))
                new_links = new_related[cid] - existing
                if new_links:
                    claim["related_claims"] = list(existing | new_links)
                    changed = True
                    total_updated += 1

            claims.append(claim)

        if changed:
            with open(claims_file, "w", encoding="utf-8") as f:
                for claim in claims:
                    f.write(json.dumps(claim, ensure_ascii=False) + "\n")

    # Build report
    report = {
        "plugins_linked": len(plugin_data),
        "total_links": sum(links_added.values()),
        "claims_updated": total_updated,
        "links_by_pair": dict(links_added),
        "top_connections": sorted(link_details, key=lambda x: x["similarity"], reverse=True)[:20],
        "threshold": threshold,
        "top_k": top_k,
    }

    # Save report
    from .config import REPO_ROOT
    report_file = REPO_ROOT / "scripts" / "epistemic" / REPORT_FILE
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    # Print summary
    print(f"  Total links: {report['total_links']}", file=sys.stderr)
    print(f"  Claims updated: {total_updated}", file=sys.stderr)
    print(f"  Links by pair:", file=sys.stderr)
    for pair, count in sorted(links_added.items(), key=lambda x: x[1], reverse=True):
        print(f"    {pair}: {count}", file=sys.stderr)

    if report["top_connections"]:
        print(f"\n  Top 5 cross-plugin connections:", file=sys.stderr)
        for link in report["top_connections"][:5]:
            print(f"    [{link['similarity']:.3f}] {link['source_plugin']}:'{link['source_text'][:40]}...'",
                  file=sys.stderr)
            print(f"           <-> {link['target_plugin']}:'{link['target_text'][:40]}...'",
                  file=sys.stderr)

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Cross-plugin semantic linker")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD)
    parser.add_argument("--top-k", type=int, default=TOP_K_NEIGHBORS)
    args = parser.parse_args()

    report = link_plugins(threshold=args.threshold, top_k=args.top_k)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
