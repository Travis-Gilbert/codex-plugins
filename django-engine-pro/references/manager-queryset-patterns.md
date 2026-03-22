# Custom Manager and QuerySet Patterns

## The Pattern

Custom managers and QuerySets let you encapsulate query logic on the model
rather than scattering it across views and serializers. This follows the
"fat models, thin views" principle.

## Custom QuerySet with Chainable Methods

```python
from django.db import models

class ContentItemQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published", is_deleted=False)

    def by_author(self, author):
        return self.filter(author=author)

    def with_stats(self):
        return self.annotate(
            comment_count=models.Count("comments"),
            avg_rating=models.Avg("ratings__score"),
        )

    def recent(self, days=30):
        from django.utils import timezone
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

class ContentItemManager(models.Manager):
    def get_queryset(self):
        return ContentItemQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

class ContentItem(models.Model):
    objects = ContentItemManager()

    # Chainable usage:
    # ContentItem.objects.published().by_author(user).with_stats()
    # ContentItem.objects.published().recent(7)
```

## as_manager() Shortcut

```python
class ContentItemQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")

class ContentItem(models.Model):
    objects = ContentItemQuerySet.as_manager()
```

## SoftDelete Manager Pattern

```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Soft-delete: set is_deleted=True instead of DELETE."""
        return self.update(is_deleted=True)

    def hard_delete(self):
        """Actually delete from database."""
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

class BaseModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Includes deleted

    class Meta:
        abstract = True
```

## django-model-utils Patterns

### InheritanceManager
```python
from model_utils.managers import InheritanceManager

class ContentItem(models.Model):
    objects = InheritanceManager()

# Returns actual child instances (like polymorphic, but lighter):
ContentItem.objects.select_subclasses()
```

### StatusField + StatusManager
```python
from model_utils.fields import StatusField
from model_utils import Choices

class Article(models.Model):
    STATUS = Choices("draft", "published", "archived")
    status = StatusField()
```

### TimeStampedModel
```python
from model_utils.models import TimeStampedModel

class Article(TimeStampedModel):
    # Gets created and modified fields automatically
    title = models.CharField(max_length=200)
```

## Anti-Patterns

1. **Filtering in views instead of managers**: If you always filter `is_deleted=False`,
   put it in the default manager
2. **Managers that return different model types**: A manager's queryset should always
   return instances of its own model
3. **Too many managers**: More than 2-3 managers on a model is a smell. Use QuerySet
   methods instead and chain them
4. **Forgetting as_manager()**: If you only need chainable methods and no custom
   Manager logic, `QuerySet.as_manager()` is simpler
