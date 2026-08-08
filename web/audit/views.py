from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.views.generic import ListView

from .models import AuditLog

User = get_user_model()


class AdminRequiredMixin(UserPassesTestMixin):
    """Zabezpieczenie: tylko admin/superuser ma dostęp do logów."""

    def test_func(self):
        return (
            self.request.user.is_superuser
            or getattr(self.request.user, "role", "") == "admin"
        )


class AuditLogListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = (
        "audit/audit_log_list.html"  # Zmień ścieżkę według struktury Twoich katalogów
    )
    paginate_by = 15
    context_object_name = "logs"
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()

        # Wyszukiwanie
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(table_name__icontains=q) | Q(record_id__icontains=q))

        # Filtrowanie po operacji
        operation = self.request.GET.get("operation", "")
        if operation:
            qs = qs.filter(operation=operation)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        logs = context["logs"]
        user_ids = [log.user_id for log in logs if log.user_id]

        if user_ids:
            users = User.objects.filter(id__in=user_ids).values("id", "username")
            user_map = {user["id"]: user["username"] for user in users}
        else:
            user_map = {}

        for log in logs:
            if log.user_id:
                log.username = user_map.get(
                    log.user_id, f"ID: {log.user_id} (Usunięty)"
                )
            else:
                log.username = "System/Brak"

        context["current_search"] = self.request.GET.get("q", "")
        context["current_operation"] = self.request.GET.get("operation", "")
        context["operations"] = ["INSERT", "UPDATE", "DELETE"]

        return context
