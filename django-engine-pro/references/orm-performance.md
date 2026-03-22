# Django ORM Performance Playbook

## The Six Anti-Patterns

### 1. N+1 Queries

**Signal**: A loop that accesses a related object without prefetching.

```python
# BAD: N+1 — one query per item for item.author
for item in ContentItem.objects.all():
    print(item.author.name)  # SQL query per iteration

# GOOD: select_related for ForeignKey/OneToOne forward
for item in ContentItem.objects.select_related("author").all():
    print(item.author.name)  # No extra queries
```

### 2. Missing Prefetch for Reverse Relations

```python
# BAD: N+1 on reverse FK / M2M
for author in Author.objects.all():
    print(author.articles.count())  # Query per author

# GOOD: prefetch_related for reverse FK, M2M, GenericRelation
for author in Author.objects.prefetch_related("articles").all():
    print(author.articles.count())  # Uses prefetched cache
```

### 3. Unfiltered Prefetch

```python
# BAD: prefetches ALL tags, even inactive ones
Author.objects.prefetch_related("articles__tags")

# GOOD: filtered prefetch with Prefetch object
from django.db.models import Prefetch
Author.objects.prefetch_related(
    Prefetch("articles__tags", queryset=Tag.objects.filter(active=True))
)
```

### 4. Python Aggregation

```python
# BAD: fetches all rows to Python, then sums
total = sum(item.price for item in Order.objects.all())

# GOOD: database aggregation
from django.db.models import Sum
total = Order.objects.aggregate(total=Sum("price"))["total"]
```

### 5. Unnecessary Evaluation

```python
# BAD: evaluates entire queryset just to check existence
if queryset:  # Loads all rows!
    ...

# GOOD:
if queryset.exists():  # SQL EXISTS, stops at first match
    ...

# BAD: loads all rows to count
count = len(queryset)

# GOOD:
count = queryset.count()  # SQL COUNT
```

### 6. Over-fetching Columns

```python
# BAD: fetches all 30 columns when you need 3
items = ContentItem.objects.all()

# GOOD: project only needed columns
items = ContentItem.objects.only("id", "title", "created_at")

# GOOD: exclude heavy columns
items = ContentItem.objects.defer("body", "raw_html")
```

## Performance Verification Tools

### django-debug-toolbar
Shows query count and timing per request. Essential for development.

### EXPLAIN ANALYZE
```python
from django.db import connection
qs = ContentItem.objects.filter(status="published").select_related("author")
print(qs.query)  # See the SQL
# Then run EXPLAIN ANALYZE in psql/pgcli
```

### Query Logging
```python
# In settings.py for development
LOGGING = {
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    }
}
```

### connection.queries
```python
from django.db import connection, reset_queries
reset_queries()
# ... run your code ...
print(f"Queries: {len(connection.queries)}")
for q in connection.queries:
    print(f"  {q['time']}s: {q['sql'][:100]}")
```

## Indexing Strategy

- **Always index**: Fields used in `filter()`, `order_by()`, `distinct()`
- **Consider composite indexes**: For multi-column lookups `(status, created_at)`
- **Partial indexes**: For sparse conditions `Index(condition=Q(is_deleted=False))`
- **GIN indexes**: For JSONField and ArrayField lookups on PostgreSQL
- **Covering indexes**: `Index(fields=["status"], include=["title"])` to avoid table lookups

## Window Functions

```python
from django.db.models import F, Window
from django.db.models.functions import Rank, RowNumber, Lag

# Rank within a partition
ContentItem.objects.annotate(
    rank=Window(
        expression=Rank(),
        partition_by=F("category"),
        order_by=F("score").desc(),
    )
)
```
