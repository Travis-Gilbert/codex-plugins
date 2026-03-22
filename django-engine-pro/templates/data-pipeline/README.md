# Data Pipeline Template

Reusable pattern for: QuerySet extraction (with field specification and
chunking), pandas/numpy computation, and bulk_create write-back with
transaction safety.

## Files

- `pipeline.py` — Extract-compute-load pipeline with memory-aware extraction
- `schemas.py` — Pydantic validation at pipeline boundaries

## Memory Strategy

| Data Volume | Method |
|-------------|--------|
| <10K rows | values() + DataFrame |
| 10K-100K | values_list(named=True) |
| 100K+ | read_sql_query(chunksize) |
