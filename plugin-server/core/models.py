from django.db import models


class ActiveManager(models.Manager):
    """Default manager that excludes soft-deleted rows."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimestampedModel(models.Model):
    """Abstract base. Shared timestamps, soft-delete."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
