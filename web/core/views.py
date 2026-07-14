from decimal import Decimal

from companies.models import Companies
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse
from django.views.generic import TemplateView
from emissions.models import (
    EnergyConsumption,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)
from what_if.models import ReductionTarget
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

    @staticmethod
    def get_target_chart_data(target):
        years = list(range(target.base_year, target.target_year + 1))
        s1_data = []
        s2_data = []

        for y in years:
            qs_filters = {"company": target.company, "year": y}

            mob = (
                MobileCombustion.objects.filter(**qs_filters).aggregate(
                    t=Sum("emission_tco2eq")
                )["t"]
                or 0
            )
            stat = (
                StationaryCombustion.objects.filter(**qs_filters).aggregate(
                    t=Sum("emission_tco2eq")
                )["t"]
                or 0
            )
            proc = (
                ProcessEmission.objects.filter(**qs_filters).aggregate(
                    t=Sum("emission_tco2eq")
                )["t"]
                or 0
            )
            fug = (
                FugitiveEmission.objects.filter(**qs_filters).aggregate(
                    t=Sum("emission_tco2eq")
                )["t"]
                or 0
            )
            s1 = float(mob + stat + proc + fug)
            s2 = float(
                EnergyConsumption.objects.filter(**qs_filters).aggregate(
                    t=Sum("emission_tco2eq")
                )["t"]
                or 0
            )

            s1_data.append(s1)
            s2_data.append(s2)

        current_year_idx = min(len(s1_data) - 1, 0)
        total_val = s1_data[-1] + s2_data[-1] if (s1_data and s2_data) else 0

        status = "green"
        return {
            "years": years,
            "s1": s1_data,
            "s2": s2_data,
            "current_emission": total_val,
            "target_emission": float(s1_data[0] + s2_data[0])
            * (1 - float(target.reduction_pct) / 100),
            "status_color": status,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == "admin" or user.is_superuser:
            allowed_companies = Companies.objects.all()
        else:
            allowed_companies = Companies.objects.filter(
                user_permissions__user=user, user_permissions__can_read=True
            ).distinct()

        targets = ReductionTarget.objects.filter(
            company__in=allowed_companies
        ).select_related("company", "goal")

        # Przygotowanie danych dla każdego celu
        for target in targets:
            target.chart_data = self.get_target_chart_data(target)

        context["reduction_targets"] = targets

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
