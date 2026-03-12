# Scientific Python

## Numerical and Tabular Work
- Prefer NumPy arrays for tight numerical kernels and vectorized operations.
- Prefer pandas for schema-aware tabular transforms, joins, feature prep, and data inspection.
- Use SciPy when the task is fundamentally numerical analysis, optimization, interpolation, sparse math, or statistics.
- State data size, shape, sparsity, missingness, and dtype assumptions before optimizing.

## Classical Data Science
- Reach for scikit-learn first when the task is TF-IDF, linear models, clustering, dimensionality reduction, or pipeline composition.
- Prefer sparse pipelines for text features when dimensionality is high.
- Treat BM25, TF-IDF, and keyword overlap as production-safe baselines before reaching for deep models.
- Evaluate with held-out data or at least a fixed fixture set; do not declare improvement from eyeballing a few outputs.

## Statistical Modeling
- Use SciPy stats for standard tests, distributions, and descriptive analysis.
- Use PyMC or Bayesian methods when uncertainty estimation or online updating matters more than point estimates.
- Prefer simple models that explain the signal unless the task explicitly calls for richer inference.
- Report effect size, uncertainty, and practical significance, not only p-values.

## NLP, Embeddings, and Retrieval
- Use spaCy for tokenization, rule-based extraction, classic NER, and lightweight semantic features.
- Use sentence-transformers when sentence-level semantics or retrieval quality matters more than deterministic transparency.
- Choose FAISS index type based on corpus size and memory budget:
  - `<1K`: exact search is fine
  - `1K-50K`: IVF is usually enough
  - `50K+`: compressed or specialized ANN becomes necessary
- Keep fallback retrieval paths when semantic dependencies are unavailable.

## Graph Science
- Use NetworkX for correctness, prototyping, and moderate graph sizes.
- Move to faster graph tooling only when graph size or runtime justifies it.
- Separate graph construction, weighting, and algorithm choice so each can be tested independently.
- For discovery systems, explain why an edge exists; raw score output is not enough.

## Implementation Standards
- Prefer vectorization over Python loops when it materially improves clarity or runtime.
- Benchmark before claiming speedups.
- Guard against silent shape mismatches, dtype surprises, and memory blowups.
- On production paths, prefer deterministic preprocessing, cacheable features, and explainable thresholds.
