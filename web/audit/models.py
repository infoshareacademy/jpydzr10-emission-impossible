from django.db import models


class AuditLog(models.Model):
    table_name = models.CharField(max_length=200, db_index=True)
    operation = models.CharField(max_length=10)
    record_id = models.CharField(max_length=50, db_index=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_log"
        verbose_name = "Log zmian"
        verbose_name_plural = "Logi zmian"
        indexes = [
            models.Index(fields=["table_name", "record_id"]),
        ]

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.operation} on {self.table_name} #{self.record_id}"
