# Django Model Inheritance Strategies

## The Four Patterns

### 1. Abstract Base Classes

**What**: Shared fields and methods defined on a base class with `abstract = True`. No database table for the base. Each child gets its own table with all fields.

**Use when**:
- Multiple models share fields (timestamps, status, slug)
- No need to query across child types
- No need for a shared ForeignKey target

**Cost**: None at query time. Each child is independent.

**Trade-off**: Cannot do `BaseModel.objects.all()` to get mixed types. Cannot have a ForeignKey pointing to the abstract base.

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Essay(TimeStampedModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
```

### 2. Multi-Table Inheritance

**What**: Each model in the hierarchy gets its own table. Django creates an implicit OneToOneField linking child to parent. Parent table is queryable directly.

**Use when**:
- Need to query the parent table directly
- Each child adds its own columns
- Want a shared ForeignKey target (point to the parent)

**Cost**: Extra JOIN per inheritance level on every child query. Parent table query returns only base fields (no automatic downcasting).

**Trade-off**: JOINs add latency. Parent.objects.all() returns base instances, not child types. Use django-model-utils InheritanceManager for `.select_subclasses()` if you need downcasting (but consider django-polymorphic instead).

```python
class ContentItem(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Essay(ContentItem):
    body = models.TextField()
    word_count = models.IntegerField(default=0)
```

### 3. Proxy Models

**What**: Same database table, different Python class. The proxy model can have different managers, methods, ordering, and Meta options.

**Use when**:
- Same data, different behavior
- Need different default ordering or managers for different views
- Admin needs different interfaces for the same data

**Cost**: None at query time. Same table, same queries.

**Trade-off**: Cannot add fields. The proxy and the original share the exact same columns.

```python
class ContentItem(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="draft")

class PublishedContent(ContentItem):
    class Meta:
        proxy = True
        ordering = ["-created_at"]

    objects = PublishedManager()  # filters to status="published"
```

### 4. django-polymorphic

**What**: Multi-table inheritance with automatic downcasting. `Parent.objects.all()` returns correctly-typed child instances by joining on ContentType.

**Use when ALL four conditions are met**:
1. Single queryset returning mixed types
2. Each type has own additional fields
3. Need actual subclass instances (not just base fields)
4. Type count is bounded and grows slowly

**Cost**: ContentType JOIN on every polymorphic query + child table JOINs for downcasting. Use `.non_polymorphic()` to skip when only base fields needed.

**Trade-off**: Most expensive inheritance pattern. Requires django-polymorphic package. Migration complexity increases. But it's the ONLY pattern that gives you mixed-type querysets with automatic downcasting.

```python
from polymorphic.models import PolymorphicModel

class ContentItem(PolymorphicModel):
    title = models.CharField(max_length=200)

class Essay(ContentItem):
    body = models.TextField()

class FieldNote(ContentItem):
    location = models.CharField(max_length=200)
    observation = models.TextField()

# This returns Essay and FieldNote instances, not ContentItem:
ContentItem.objects.all()
```

## Decision Tree

```
Do you need to query across child types in a single queryset?
├── No → Abstract Base Class
└── Yes → Do children add their own fields?
    ├── No → Proxy Model
    └── Yes → Do you need the actual child instance (not just base fields)?
        ├── No → Multi-Table Inheritance (query parent table only)
        └── Yes → django-polymorphic
```

## Common Mistakes

1. **Using multi-table when abstract would suffice**: If you never query `Parent.objects.all()`, abstract is always better (no JOINs).

2. **Using polymorphic for two types**: If there are only 2-3 types and the list is fixed, consider a discriminated union (single table with a `type` field and nullable type-specific columns) instead. Polymorphic shines when the type hierarchy is rich.

3. **Forgetting non_polymorphic()**: Every polymorphic query pays the ContentType JOIN cost. If you only need `title` and `created_at`, use `.non_polymorphic().only("title", "created_at")`.

4. **Not considering the admin**: Polymorphic admin requires PolymorphicParentModelAdmin + PolymorphicChildModelAdmin. Multi-table admin is simpler. Abstract base admin is simplest (each child has its own admin).
