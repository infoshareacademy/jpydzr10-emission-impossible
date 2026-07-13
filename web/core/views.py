from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from workflow.models import Task

from core.models import UserPageView

from .registry import APPS_REGISTRY


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    DEFAULT_SHORTCUTS = [
        "reports:ghg-report",
        "emissions:factor-list",
        "ai_services:global_assistant",
        "communications:thread_list",
    ]

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

            top_user_views = list(
                UserPageView.objects.filter(user=user)
                .order_by("-visit_count")
                .values("view_name", "url_path")[:4]
            )

            registry_map = {item["url_name"]: item for item in APPS_REGISTRY}

            shortcuts_for_template = []
            for item in top_user_views:
                meta = registry_map.get(item["view_name"])
                if meta:
                    shortcuts_for_template.append(
                        {
                            "title": meta["title"],
                            "icon": meta["icon"],
                            "url": item["url_path"],
                        }
                    )
            if not shortcuts_for_template:
                for url_name in self.DEFAULT_SHORTCUTS:
                    meta = registry_map.get(url_name)
                    if meta:
                        shortcuts_for_template.append(
                            {
                                "title": meta["title"],
                                "icon": meta["icon"],
                                "url": reverse(url_name),
                            }
                        )
            context["favorite_shortcuts"] = shortcuts_for_template
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"
