# Django + Scientific Python Integration

## The Bridge Problem

Django's ORM speaks in model instances and querysets. Scientific Python speaks in
arrays and DataFrames. The bridge between them has performance traps at every step:
extraction (too many columns), conversion (too much memory), and write-back
(row-by-row saves).

## Extraction Patterns

### Small Tables (<10,000 rows)
```python
import pandas as pd

df = pd.DataFrame(
    Observation.objects.filter(
        experiment_id=42
    ).values("id", "timestamp", "value", "unit")
)
```

### Medium Tables (10,000-100,000 rows)
```python
qs = Observation.objects.filter(
    experiment_id=42
).values_list("id", "timestamp", "value", "unit", named=True)

df = pd.DataFrame.from_records(qs, columns=["id", "timestamp", "value", "unit"])
```

### Large Tables (100,000+ rows)
```python
from django.db import connection

qs = Observation.objects.filter(experiment_id=42)
chunks = []
for chunk in pd.read_sql_query(str(qs.query), connection, chunksize=10000):
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
```

### Using django-pandas
```python
from django_pandas.io import read_frame

df = read_frame(
    Observation.objects.filter(experiment__status="complete"),
    fieldnames=["id", "timestamp", "value", "unit"],
    index_col="id"
)
```

## Write-Back Patterns

### Bulk Create with NaN Handling
```python
from django.db import transaction

def ingest_results(df: pd.DataFrame, experiment_id: int) -> int:
    df = df.where(pd.notna(df), None)  # NaN -> None for Django

    instances = [
        Result(
            experiment_id=experiment_id,
            metric=row["metric"],
            value=row["value"],
        )
        for _, row in df.iterrows()
    ]

    with transaction.atomic():
        created = Result.objects.bulk_create(instances, batch_size=1000)
    return len(created)
```

### Update or Create
```python
def upsert_summaries(df: pd.DataFrame) -> tuple[int, int]:
    created_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        _, created = ExperimentSummary.objects.update_or_create(
            experiment_id=row["experiment_id"],
            defaults={
                "mean": row["mean"],
                "std": row["std"],
                "n": row["n"],
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    return created_count, updated_count
```

## Computation Pipeline Template

```python
import numpy as np
from scipy import stats

def compute_statistics(experiment_id: int) -> dict:
    """Extract -> Compute -> Store pipeline."""

    # 1. Extract (minimal columns, no model instantiation)
    values = list(
        Observation.objects.filter(
            experiment_id=experiment_id
        ).values_list("value", flat=True)
    )
    arr = np.array(values, dtype=np.float64)

    # 2. Compute
    result = {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)),
        "median": float(np.median(arr)),
        "skew": float(stats.skew(arr)),
        "kurtosis": float(stats.kurtosis(arr)),
        "n": len(arr),
    }

    # 3. Store
    ExperimentSummary.objects.update_or_create(
        experiment_id=experiment_id,
        defaults=result,
    )
    return result
```

## Memory Rules

| Data Volume | Extraction Method | Memory Impact |
|-------------|------------------|---------------|
| <10K rows | values() + DataFrame | Low |
| 10K-100K | values_list(named=True) | Medium |
| 100K+ | read_sql_query(chunksize) | Controlled |
| Single column | values_list(flat=True) | Minimal |

**Never**: `list(Model.objects.all())` on large tables
**Always**: Specify exact fields, use batch_size for writes

## Jupyter Integration (dj-notebook)

```python
# In a Jupyter notebook
from dj_notebook import activate
plus = activate()

# Now you have full Django ORM access
from myapp.models import Observation
df = plus.read_frame(Observation.objects.filter(status="complete"))
df.describe()
```
