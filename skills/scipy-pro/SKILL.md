---
name: scipy-pro
description: Scientific Python and data science implementation skill with source-verified workflows for NumPy, SciPy, pandas, scikit-learn, statistics, NLP, embeddings, vector search, graph science, and knowledge-system engineering. Use when Codex needs to build, debug, benchmark, refactor, or review scientific Python, data analysis, ML pipelines, semantic search, knowledge graphs, research tooling, or data-intensive backends, especially when verifying behavior against upstream library source or the research_api/CommonPlace architecture matters.
---

# SciPy Pro

## Workflow
1. Classify the task by tier.
- Tier 1: general scientific Python or data science technique.
- Tier 2: applying the technique to a knowledge system, connection engine, graph pipeline, semantic search stack, or claim-analysis workflow.
- Tier 3: research_api or CommonPlace product, API, ingestion, or deployment work.

2. Prefer source over memory.
- Run `scripts/bootstrap_refs.sh --dry-run` to inspect the default reference set.
- Clone or update refs only when the task depends on concrete library behavior.
- Grep actual implementations before writing framework-specific code.

3. Load only the relevant reference file.
- Routing and reference selection: `references/routing.md`
- Numerical, statistical, NLP, embedding, and graph work: `references/scientific-python.md`
- Connection engines, KGE, claims, resurfacing, and self-organization: `references/knowledge-systems.md`
- Deployment, API, ingestion, and graceful degradation: `references/product-and-ops.md`

4. Read the target codebase.
- For `research_api`, the live source is authoritative, not the spec.
- Confirm dependency versions from lockfiles, `pyproject.toml`, or `requirements` before relying on APIs.

5. Implement with production discipline.
- Prefer vectorized and numerically stable code.
- Separate exploratory notebooks from importable production modules.
- Add benchmarks, sampling strategy, and evaluation criteria for model or data work.
- Add fallback paths when advanced ML dependencies may be absent.

6. Validate.
- Run tests, micro-benchmarks, or small fixture checks.
- On data or ML tasks, state assumptions about scale, sparsity, class balance, latency, and memory.

## Guardrails
- Do not guess upstream library behavior when the source is available.
- Do not introduce GPU-only or PyTorch-only paths without a CPU-safe fallback when the environment may be constrained.
- Do not replace deterministic or interpretable methods with heavy ML unless the quality gain is justified.
- Do not treat architecture docs as canonical without reading the live files they describe.

## Quick Triggers
Use this skill for requests such as:
- "Build a scientific Python pipeline for feature extraction and clustering."
- "Tune FAISS or sentence-transformers for semantic search."
- "Add a new pass to a connection or compose engine."
- "Review a data science or graph algorithm implementation."
- "Make this research pipeline production-safe on limited hardware."
