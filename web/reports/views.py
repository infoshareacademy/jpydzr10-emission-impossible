import json

from accounts.models import UserCompanyPermission
from companies.models import Companies
from core.mixins import PageViewTrackerMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView
from emissions.models import (
    EnergyConsumption,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)
from workflow.models import WorkflowStatusMixin

EMISSION_FIELDS = {
    "calculated": "calculated_emission_tco2eq",
    "declared": "emission_tco2eq",
}

DEFAULT_STATUSES = [choice[0] for choice in WorkflowStatusMixin.RecordStatus.choices]


class GHGReportView(PageViewTrackerMixin, LoginRequiredMixin, TemplateView):
    template_name = "reports/ghg_report.html"

    def get_accessible_companies(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Companies.objects.all().order_by("name")
        perm_company_ids = UserCompanyPermission.objects.filter(user=user).values_list(
            "company_id", flat=True
        )
        return Companies.objects.filter(id__in=perm_company_ids).order_by("name")

    def get_emissions_for_scope(self, company_ids, year, selected_statuses, emission_field):
        s1_total = 0
        for model in [
            StationaryCombustion,
            MobileCombustion,
            ProcessEmission,
            FugitiveEmission,
        ]:
            result = model.objects.filter(
                company_id__in=company_ids,
                year=year,
<<<<<<< HEAD
                workflow_status__in=statuses,
=======
                workflow_status__in=selected_statuses,
>>>>>>> origin/main
            ).aggregate(total=Sum(emission_field))
            s1_total += result["total"] or 0

        s2_result = EnergyConsumption.objects.filter(
            company_id__in=company_ids,
            year=year,
<<<<<<< HEAD
            workflow_status__in=statuses,
=======
            workflow_status__in=selected_statuses,
>>>>>>> origin/main
        ).aggregate(total=Sum(emission_field))
        s2_total = s2_result["total"] or 0

        return float(s1_total), float(s2_total)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        accessible_companies = self.get_accessible_companies()
        accessible_company_ids = list(accessible_companies.values_list("id", flat=True))

        # Parametry GET
        selected_company_id = self.request.GET.get("company", "all")
        selected_year = self._safe_int(self.request.GET.get("year"), 2024)
        compare_year = self._safe_int(
            self.request.GET.get("compare_year"), selected_year - 1
        )

        emission_source = self.request.GET.get("emission_source", "calculated")
        if emission_source not in EMISSION_FIELDS:
            emission_source = "calculated"
        emission_field = EMISSION_FIELDS[emission_source]

        if "statuses" in self.request.GET:
            valid_statuses = [
                choice[0] for choice in WorkflowStatusMixin.RecordStatus.choices
            ]
            selected_statuses = [
                s for s in self.request.GET.getlist("statuses") if s in valid_statuses
            ]
        else:
            selected_statuses = DEFAULT_STATUSES

        if selected_company_id != "all" and selected_company_id.isdigit():
            cid = int(selected_company_id)
            if cid in accessible_company_ids:
                company_ids_to_calc = [cid]
            else:
                company_ids_to_calc = accessible_company_ids
                selected_company_id = "all"
        else:
            company_ids_to_calc = accessible_company_ids

        if selected_statuses and company_ids_to_calc:
            # Wykres: trend 3-letni (selected_year-2, selected_year-1, selected_year)
            trend_years = [selected_year - 2, selected_year - 1, selected_year]
            trend_data = []
            for yr in trend_years:
                s1, s2 = self.get_emissions_for_scope(
                    company_ids_to_calc, yr, selected_statuses, emission_field
                )
                trend_data.append(
                    {
                        "year": yr,
                        "s1": round(float(s1), 2),
                        "s2": round(float(s2), 2),
                        "total": round(float(s1 + s2), 2),
                    }
                )

            # KPI bieżący rok = ostatni w trendzie
            s1_current = trend_data[2]["s1"]
            s2_current = trend_data[2]["s2"]
            total_current = trend_data[2]["total"]

            # KPI porównanie = rok wybrany przez użytkownika w formularzu
            s1_cmp, s2_cmp = self.get_emissions_for_scope(
                company_ids_to_calc, compare_year, selected_statuses, emission_field
            )
            s1_compare = round(float(s1_cmp), 2)
            s2_compare = round(float(s2_cmp), 2)
            total_compare = round(s1_compare + s2_compare, 2)
        else:
            trend_years = [selected_year - 2, selected_year - 1, selected_year]
            trend_data = [
                {"year": yr, "s1": 0.0, "s2": 0.0, "total": 0.0} for yr in trend_years
            ]
            s1_current = s2_current = total_current = 0.0
            s1_compare = s2_compare = total_compare = 0.0

        if total_compare > 0:
            reduction_pct = ((total_current - total_compare) / total_compare) * 100
        else:
            reduction_pct = 0

        context.update(
            {
                "companies": accessible_companies,
                "selected_company": selected_company_id,
                "selected_year": selected_year,
                "compare_year": compare_year,
                "emission_source": emission_source,
                "selected_statuses": selected_statuses,
                "all_statuses": WorkflowStatusMixin.RecordStatus.choices,
                "s1_current": round(s1_current, 2),
                "s2_current": round(s2_current, 2),
                "total_current": round(total_current, 2),
                "s1_compare": round(s1_compare, 2),
                "s2_compare": round(s2_compare, 2),
                "total_compare": round(total_compare, 2),
                "reduction_pct": round(reduction_pct, 2),
                "chart_data_json": json.dumps(
                    {
                        "years": trend_years,
                        "s1": [d["s1"] for d in trend_data],
                        "s2": [d["s2"] for d in trend_data],
                    }
                ),
                "has_data": (total_current > 0 or total_compare > 0),
                "form_submitted": "statuses" in self.request.GET,
                "no_statuses_selected": len(selected_statuses) == 0,
            }
        )
        return context

    @staticmethod
    def _safe_int(value, default):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
