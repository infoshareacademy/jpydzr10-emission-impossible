from django.conf import settings
from django.db import models


class CoreModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )
    note = models.TextField(blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ChangeLog(models.Model):
    id_rejestr_zmian = models.AutoField(primary_key=True)
    login = models.CharField(max_length=100)
    date_change = models.DateTimeField()
    table_name = models.CharField(max_length=200)
    record_id = models.CharField(max_length=50)
    change_type = models.CharField(max_length=10)
    previous_data = models.TextField(blank=True, null=True)
    actual_data = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "tbl_change_log"
        verbose_name = "Log zmian"
        verbose_name_plural = "Logi zmian"
