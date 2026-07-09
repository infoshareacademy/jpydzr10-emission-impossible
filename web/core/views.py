from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from workflow.models import Task

from core.models import UserPageView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            context["favorite_shortcuts"] = UserPageView.objects.filter(
                user=user
            ).order_by("-visit_count")[:5]

            if user.is_staff or user.is_superuser:
                context["tasks"] = Task.objects.filter(is_completed=False)
            else:
                context["tasks"] = Task.objects.filter(
                    assigned_to=user, is_completed=False
                )

        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"
