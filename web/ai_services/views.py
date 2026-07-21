from companies.models import Companies
from core.mixins import PageViewTrackerMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class GlobalAIAssistantView(PageViewTrackerMixin, LoginRequiredMixin, TemplateView):
    template_name = "ai_services/global_chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == "admin" or user.is_superuser:
            context["companies"] = Companies.objects.all().order_by("name")
        else:
            context["companies"] = (
                Companies.objects.filter(
                    user_permissions__user=user, user_permissions__can_read=True
                )
                .distinct()
                .order_by("name")
            )
        return context