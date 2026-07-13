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
            if user.is_staff or user.is_superuser:
                tasks_qs = (
                    Task.objects.filter(is_completed=False)
                    .select_related("company")
                    .order_by("-deadline")
                )
            else:
                tasks_qs = (
                    Task.objects.filter(assigned_to=user, is_completed=False)
                    .select_related("company")
                    .order_by("-deadline")
                )

            grouped_tasks = {}
            for task in tasks_qs:
                key = task.title
                if key not in grouped_tasks:
                    grouped_tasks[key] = {
                        "title": task.title,
                        "description": task.description,
                        "deadline": task.deadline,
                        "tasks": [],
                    }
                grouped_tasks[key]["tasks"].append(task)

            context["grouped_tasks"] = grouped_tasks.values()
            context["favorite_shortcuts"] = UserPageView.objects.filter(
                user=user
            ).order_by("-visit_count")[:5]

        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"
