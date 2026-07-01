from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import AuditLog

User = get_user_model()


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "table_name",
        "operation",
        "record_id",
        "user_display",
    )
    list_filter = ("operation", "table_name", "created_at")
    search_fields = ("table_name", "record_id", "user_id")
    readonly_fields = (
        "table_name",
        "operation",
        "record_id",
        "old_data",
        "new_data",
        "user_id",
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description="Użytkownik", ordering="user_id")
    def user_display(self, obj):
        if obj.user_id is None:
            return "—"
        user = User.objects.filter(pk=obj.user_id).only("username").first()
        return user.username if user else f"ID {obj.user_id} (usunięty)"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
