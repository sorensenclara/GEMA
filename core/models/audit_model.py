from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from core.middleware import get_current_user


class AuditModel(models.Model):
    """
    Abstract base model that automatically tracks creation and modification
    information (timestamp and user) for auditing purposes, and keeps a full
    history of changes via django-simple-history.
    """
    history = HistoricalRecords(inherit=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el", editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
        verbose_name="Creado por",
        editable=False,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modificado el", editable=False)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(class)s_updated",
        verbose_name="Modificado por",
        editable=False,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)
