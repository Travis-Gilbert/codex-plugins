# Product and Ops

## Deployment Contract
- Production on constrained CPU environments should keep deterministic NLP and classical ML available.
- Advanced PyTorch, SBERT, NLI, and KGE features must degrade gracefully when unavailable.
- Heavy jobs belong on a worker or offloaded environment such as Modal, not the request path.

## Graceful Degradation Pattern
```python
try:
    from apps.research.advanced_nlp import sentence_similarity
except Exception:
    sentence_similarity = None
```

- Import advanced features lazily.
- Skip or downgrade a pass rather than breaking the whole pipeline.
- Surface degraded state to callers when the feature materially affects output quality.

## API and Background Work
- Keep API handlers thin; move heavy NLP, vector rebuilds, or training into tasks.
- Treat serializer shape, pagination, and status reporting as product behavior, not incidental details.
- For webhook or async APIs, report job status and failure reason clearly.

## Ingestion
- Separate fast metadata extraction from heavy enrichment.
- Keep OCR, PDF parsing, scraping, and code parsing isolated so failures do not poison the whole ingest path.
- Persist enough provenance to explain where a derived claim, object, or edge came from.

## Operational Checks
- Estimate memory cost before adding large embedding models or ANN indexes.
- Check whether the workload is CPU-bound, IO-bound, or GPU-worthy before changing architecture.
- Record benchmark baselines when changing model size, batch size, or index type.
- On retrieval systems, track both quality metrics and latency.
