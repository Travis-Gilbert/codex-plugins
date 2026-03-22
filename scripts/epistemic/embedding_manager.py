"""Stage 6: Embedding Manager.

Generates and stores SBERT embeddings for all claims. Pre-computation
means Claude Code loads the .npz at session start and does cosine
similarity with numpy — no ML inference during sessions.

Model: all-MiniLM-L6-v2 (384-dim, CPU, <1ms per claim)
Storage: knowledge/embeddings.npz (numpy compressed archive)

Note: numpy's .npz format uses its own binary format, not pickle.
The allow_pickle=True flag is needed only for object arrays (claim_ids)
and is safe here since we control the data source (our own JSONL files).

Usage:
    python -m scripts.epistemic.embedding_manager django-design
    python -m scripts.epistemic.embedding_manager --all
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from .config import CLAIMS_FILE, knowledge_path, PLUGINS, plugin_path


# Model name — small, fast, CPU-friendly
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
EMBEDDINGS_FILE = "embeddings.npz"

# Lazy-loaded model singleton
_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"  Loading {MODEL_NAME}...", file=sys.stderr)
        _model = SentenceTransformer(MODEL_NAME)
    return _model


# ---------------------------------------------------------------------------
# Core embedding operations
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts using SBERT. Returns (N, 384) array."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between two arrays.

    Args:
        a: (N, D) or (D,) array
        b: (M, D) or (D,) array

    Returns:
        (N, M) similarity matrix, or scalar if both 1-D.
    """
    if a.ndim == 1:
        a = a.reshape(1, -1)
    if b.ndim == 1:
        b = b.reshape(1, -1)

    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return a_norm @ b_norm.T


# ---------------------------------------------------------------------------
# Plugin-level operations
# ---------------------------------------------------------------------------

def embed_plugin(plugin_name: str, force: bool = False) -> dict:
    """Generate embeddings for all claims in a plugin.

    Args:
        plugin_name: Plugin to embed.
        force: If True, re-embed all claims. If False, only embed new ones.

    Returns:
        Summary dict.
    """
    kpath = knowledge_path(plugin_name)
    claims_file = kpath / CLAIMS_FILE
    npz_file = kpath / EMBEDDINGS_FILE

    if not claims_file.exists():
        return {"error": f"No claims file for {plugin_name}"}

    # Load claims
    claims = []
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            claims.append(json.loads(line))

    if not claims:
        return {"plugin": plugin_name, "embedded": 0}

    # Load existing embeddings if not forcing
    # Note: allow_pickle is needed for the object array (claim_ids).
    # This is safe because we only load .npz files we created ourselves.
    existing_ids: dict[str, int] = {}  # claim_id -> row index
    existing_embeddings: np.ndarray | None = None
    if not force and npz_file.exists():
        data = np.load(npz_file, allow_pickle=True)
        existing_embeddings = data["embeddings"]
        if "claim_ids" in data:
            for i, cid in enumerate(data["claim_ids"]):
                existing_ids[str(cid)] = i

    # Determine which claims need embedding
    claim_ids = [c["id"] for c in claims]
    claim_texts = [c["text"] for c in claims]

    if force or existing_embeddings is None:
        texts_to_embed = claim_texts
        ids_to_embed = claim_ids
    else:
        new_indices = [i for i, cid in enumerate(claim_ids) if cid not in existing_ids]
        if not new_indices:
            _update_claim_indices(claims, claim_ids, kpath)
            return {"plugin": plugin_name, "embedded": 0, "total": len(claims), "skipped": len(claims)}
        texts_to_embed = [claim_texts[i] for i in new_indices]
        ids_to_embed = [claim_ids[i] for i in new_indices]

    # Embed
    print(f"  Embedding {len(texts_to_embed)} claims for {plugin_name}...", file=sys.stderr)
    new_embeddings = embed_texts(texts_to_embed)

    # Merge with existing
    if not force and existing_embeddings is not None and len(ids_to_embed) < len(claim_ids):
        full_embeddings = np.zeros((len(claims), EMBEDDING_DIM), dtype=np.float32)
        for i, cid in enumerate(claim_ids):
            if cid in existing_ids:
                full_embeddings[i] = existing_embeddings[existing_ids[cid]]
            else:
                new_idx = ids_to_embed.index(cid)
                full_embeddings[i] = new_embeddings[new_idx]
        all_embeddings = full_embeddings
    else:
        all_embeddings = new_embeddings.astype(np.float32)

    # Save
    np.savez_compressed(
        npz_file,
        embeddings=all_embeddings,
        claim_ids=np.array(claim_ids, dtype=object),
    )

    # Update embedding_idx on claims
    _update_claim_indices(claims, claim_ids, kpath)

    print(f"  Saved {len(claim_ids)} embeddings to {npz_file}", file=sys.stderr)
    return {
        "plugin": plugin_name,
        "embedded": len(texts_to_embed),
        "total": len(claims),
        "file": str(npz_file),
    }


def _update_claim_indices(claims: list[dict], claim_ids: list[str], kpath: Path) -> None:
    """Update embedding_idx on each claim to match the npz row index."""
    id_to_idx = {cid: i for i, cid in enumerate(claim_ids)}
    changed = False
    for claim in claims:
        new_idx = id_to_idx.get(claim["id"])
        if claim.get("embedding_idx") != new_idx:
            claim["embedding_idx"] = new_idx
            changed = True

    if changed:
        claims_file = kpath / CLAIMS_FILE
        with open(claims_file, "w", encoding="utf-8") as f:
            for claim in claims:
                f.write(json.dumps(claim, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Similarity search
# ---------------------------------------------------------------------------

def find_similar_claims(
    plugin_name: str,
    query_text: str,
    top_k: int = 10,
    threshold: float = 0.5,
) -> list[dict]:
    """Find claims most similar to a query text.

    Returns list of {claim_id, text, similarity, domain} dicts.
    """
    kpath = knowledge_path(plugin_name)
    npz_file = kpath / EMBEDDINGS_FILE
    claims_file = kpath / CLAIMS_FILE

    if not npz_file.exists():
        return []

    data = np.load(npz_file, allow_pickle=True)
    embeddings = data["embeddings"]
    claim_ids = list(data["claim_ids"])

    claims_by_id = {}
    for line in claims_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            c = json.loads(line)
            claims_by_id[c["id"]] = c

    query_emb = embed_texts([query_text])
    sims = cosine_similarity(query_emb, embeddings)[0]

    ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)
    results = []
    for idx, sim in ranked[:top_k]:
        if sim < threshold:
            break
        cid = claim_ids[idx]
        claim = claims_by_id.get(str(cid), {})
        results.append({
            "claim_id": str(cid),
            "text": claim.get("text", ""),
            "similarity": round(float(sim), 4),
            "domain": claim.get("domain", ""),
            "confidence": claim.get("confidence", 0),
        })

    return results


def load_embeddings(plugin_name: str) -> tuple[np.ndarray, list[str]] | None:
    """Load pre-computed embeddings for a plugin.

    Returns (embeddings_array, claim_ids_list) or None.
    """
    kpath = knowledge_path(plugin_name)
    npz_file = kpath / EMBEDDINGS_FILE
    if not npz_file.exists():
        return None
    data = np.load(npz_file, allow_pickle=True)
    return data["embeddings"], [str(c) for c in data["claim_ids"]]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate SBERT embeddings for plugin claims")
    parser.add_argument("plugin", nargs="?", choices=list(PLUGINS.keys()))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-embed all claims")
    args = parser.parse_args()

    if args.all:
        for name in PLUGINS:
            if plugin_path(name).exists():
                result = embed_plugin(name, force=args.force)
                print(f"  {name}: {result}", file=sys.stderr)
    elif args.plugin:
        result = embed_plugin(args.plugin, force=args.force)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
