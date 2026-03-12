# Knowledge Systems

## research_api Architecture Map
- `apps/notebook/engine.py`: 7-pass persisted connection engine
- `apps/notebook/compose_engine.py`: 6-pass live write-time discovery engine
- `apps/notebook/adaptive_ner.py`: graph-learned PhraseMatcher and cache invalidation
- `apps/notebook/bm25.py`: lexical scoring with cache-aware BM25
- `apps/notebook/vector_store.py`: FAISS-backed SBERT and KGE storage
- `apps/notebook/resurface.py`: proactive rediscovery signals
- `apps/notebook/canvas_engine.py`: Altair or Vega-Lite generation
- `apps/notebook/file_ingestion.py`: file and OCR pipeline
- `apps/research/advanced_nlp.py`: SBERT and NLI helpers
- `apps/research/connections.py`: research-side weighted signal engine
- `apps/research/tensions.py`: structural contradiction and tension logic

## The Two Engines
- `engine.py` is object-in, edges-out, and writes to the database.
- `compose_engine.py` is text-in, objects-out, and does not persist.
- Both engines should report pass state clearly to the frontend.
- Treat them as related systems, not interchangeable code paths.

## The 7-Pass Persisted Engine
1. spaCy NER and adaptive NER
2. Shared entity discovery
3. Keyword overlap or Jaccard
4. TF-IDF similarity
5. SBERT similarity, preferably via FAISS
6. NLI support or contradiction scoring
7. KGE structural similarity

## CommonPlace Rules
- `Edge.reason` must be plain English, not a code label.
- Use `from_object` and `to_object`, not `source` and `target`.
- Timeline nodes are immutable events.
- SHA-based identity and provenance are core, not optional.
- Per-notebook config controls pass activation and sensitivity.

## Adding or Changing a Pass
- Read the full engine file before inserting logic.
- Keep pass behavior isolated and nameable.
- Add configuration knobs where sensitivity or availability can vary.
- Report degraded, skipped, or complete status explicitly.
- Keep discovery, ranking, and explanation concerns separate.

## Core Tier-2 Domains
- Connection engines: multi-signal discovery and score merging
- KGE: PyKEEN training, FAISS indexing, structural similarity
- Claims: NLI, contradiction detection, and claim decomposition
- Resurfacing: proactive rediscovery signals and ranking
- Self-organization: feedback loops that reshape future discovery
