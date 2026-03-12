# Routing

## Tier Guide
| Tier | Use when | Load first |
| --- | --- | --- |
| Tier 1 | The task is about a scientific Python, statistics, NLP, embedding, or graph technique in general | `scientific-python.md` |
| Tier 2 | The task applies those techniques to a knowledge system, connection engine, semantic graph, or discovery workflow | `knowledge-systems.md` |
| Tier 3 | The task is about product constraints, API shape, ingestion, queues, or deployment in `research_api` or CommonPlace | `product-and-ops.md` |

## Domain Routing
| Task | Refs to read | Source repos to inspect after bootstrap |
| --- | --- | --- |
| NumPy, SciPy, arrays, numerical stability | `scientific-python.md` | `numpy`, `scipy` |
| pandas data prep, feature engineering, tabular analysis | `scientific-python.md` | `pandas`, `scikit-learn` |
| TF-IDF, BM25, clustering, classical ML | `scientific-python.md` | `scikit-learn`, `rank-bm25` |
| spaCy, tokenization, NER, text pipelines | `scientific-python.md` | `spacy` |
| sentence-transformers, FAISS, semantic retrieval | `scientific-python.md` | `sentence-transformers`, `faiss` |
| Graph algorithms, PageRank, communities | `scientific-python.md` | `networkx` |
| Bayesian or probabilistic modeling | `scientific-python.md` | `scipy`, `pymc` |
| 7-pass engine, compose engine, pass design | `knowledge-systems.md` | `research_api`, plus the relevant Tier 1 repo |
| KGE, PyKEEN, entity alignment | `knowledge-systems.md` | `pykeen`, `faiss`, `research_api` |
| API, Railway, Modal, RQ, ingestion | `product-and-ops.md` | `research_api`, plus the relevant Tier 1 repo |

## Source-First Rules
- If a library repo is available, grep it before relying on memory.
- If the task mentions `research_api`, `CommonPlace`, or engine file names, read the live code before the references.
- If the task spans multiple tiers, start with Tier 1 for the science, then Tier 2 for application architecture, then Tier 3 for deployment constraints.

## Grep Starting Points
- `rg "SentenceTransformer|CrossEncoder" "$HOME/.codex/cache/scipy-pro-refs/sentence-transformers"`
- `rg "IndexFlat|IndexIVF|HNSW" "$HOME/.codex/cache/scipy-pro-refs/faiss"`
- `rg "PageRank|community|betweenness" "$HOME/.codex/cache/scipy-pro-refs/networkx"`
- `rg "TfidfVectorizer|HashingVectorizer|TruncatedSVD" "$HOME/.codex/cache/scipy-pro-refs/scikit-learn"`
- `rg "Doc|EntityRuler|PhraseMatcher" "$HOME/.codex/cache/scipy-pro-refs/spacy"`
