from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, View

from workflow.models import WorkflowStatusMixin

from .models import CompanyReportEnvelope
from .services import (
    finalize_envelope_review,
    request_record_clarification,
    review_single_record,
)


class AdminRequiredMixin(UserPassesTestMixin):
    """Bezpieczeństwo: dostęp tylko dla administratorów systemu"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )


class AdminEnvelopeListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Lista wszystkich kopert raportowych w systemie dla Admina"""

    model = CompanyReportEnvelope
    template_name = "workflow/admin_envelope_list.html"
    context_object_name = "envelopes"

    def get_queryset(self):
        return CompanyReportEnvelope.objects.select_related(
            "company", "period"
        ).order_by("-period__year", "company__name")


class AdminEnvelopeReviewDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """Ekran granularnej weryfikacji wszystkich danych emisyjnych wybranej spółki"""

    model = CompanyReportEnvelope
    template_name = "workflow/admin_envelope_review.html"
    context_object_name = "envelope"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        envelope = self.get_object()
        aggregated_records = []

        for model in apps.get_models():
            if issubclass(model, WorkflowStatusMixin) and hasattr(model, "company"):
                queryset = model.objects.filter(company=envelope.company)
                if hasattr(model, "year"):
                    queryset = queryset.filter(year=envelope.period.year)
                elif hasattr(model, "date"):
                    queryset = queryset.filter(date__year=envelope.period.year)

                records = queryset.filter(
                    workflow_status__in=[
                        WorkflowStatusMixin.RecordStatus.PENDING,
                        WorkflowStatusMixin.RecordStatus.APPROVED,
                        WorkflowStatusMixin.RecordStatus.REJECTED,
                    ]
                )

                for r in records:
                    model_name = model._meta.model_name
                    admin_url = "#"

                    try:
                        if model_name == "stationarycombustion":
                            admin_url = reverse(
                                "emissions:stationarycombustion-edit",
                                kwargs={"company_id": r.company_id, "pk": r.pk},
                            )
                        elif model_name == "mobilecombustion":
                            admin_url = reverse(
                                "emissions:mobilecombustion-edit",
                                kwargs={"company_id": r.company_id, "pk": r.pk},
                            )
                        elif model_name == "processemission":
                            admin_url = reverse(
                                "emissions:processemission-edit",
                                kwargs={"company_id": r.company_id, "pk": r.pk},
                            )
                        elif model_name == "fugitiveemission":
                            admin_url = reverse(
                                "emissions:fugitiveemission-edit",
                                kwargs={"company_id": r.company_id, "pk": r.pk},
                            )

                        elif model_name == "energyconsumption":
                            admin_url = reverse(
                                "emissions:energy_consumption_edit", kwargs={"pk": r.pk}
                            )
                        elif model_name == "energypurchased":
                            admin_url = reverse(
                                "emissions:energy_purchased_edit", kwargs={"pk": r.pk}
                            )
                        elif model_name == "energyproduced":
                            admin_url = reverse(
                                "emissions:energy_produced_edit", kwargs={"pk": r.pk}
                            )
                        elif model_name == "energysold":
                            admin_url = reverse(
                                "emissions:energy_sold_edit", kwargs={"pk": r.pk}
                            )

                        else:
                            admin_url = reverse(
                                f"admin:{model._meta.app_label}_{model_name}_change",
                                args=[r.pk],
                            )

                    except Exception as e:
                        print(
                            f"[DEBUG] Nie udało się wygenerować linku dla {model_name} (ID: {r.pk}). Błąd: {e}"
                        )

                    aggregated_records.append(
                        {
                            "app_label": model._meta.app_label,
                            "model_name": model._meta.model_name,
                            "verbose_name": model._meta.verbose_name or model.__name__,
                            "instance": r,
                            "admin_url": admin_url,
                        }
                    )

        context["emission_records"] = aggregated_records
        return context


class AdminReviewActionView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Endpoint AJAX/POST do szybkiego akceptowania/odrzucania pojedynczych wierszy tabeli"""

    def post(self, request, app_label, model_name, pk):
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return JsonResponse(
                {"status": "error", "message": "Model nie istnieje"}, status=404
            )

        record = get_object_or_404(model, pk=pk)
        action = request.POST.get("action")
        reason = request.POST.get("reason", "")

        if action == "approve":
            review_single_record(record, is_approved=True, reviewer=request.user)
        elif action == "reject":
            try:
                review_single_record(
                    record, is_approved=False, reviewer=request.user, reason=reason
                )
            except ValueError as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
        else:
            return JsonResponse(
                {"status": "error", "message": "Nieprawidłowa akcja"}, status=400
            )

        return JsonResponse({"status": "success"})


class AdminFinalizeReviewView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Sfinalizowanie całego raportu spółki po przejrzeniu wszystkich wierszy"""

    def post(self, request, pk):
        envelope = get_object_or_404(CompanyReportEnvelope, pk=pk)
        try:
            result = finalize_envelope_review(envelope)
            return JsonResponse({"status": "success", "result": result})
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


class RecordClarificationView(LoginRequiredMixin, AdminRequiredMixin, View):
    """
    Endpoint POST dla admina do dodawania uwag (żądań wyjaśnienia) do konkretnego rekordu.
    """

    def post(self, request, app_label, model_name, pk):
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return JsonResponse(
                {"status": "error", "message": "Nieznany model danych."}, status=404
            )

        record = get_object_or_404(model, pk=pk)
        message = request.POST.get("message", "").strip()
        deadline = request.POST.get("deadline", "").strip()

        try:
            request_record_clarification(record, request.user, message, deadline)
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Uwaga została wysłana do użytkownika.",
                }
            )
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Wystąpił błąd krytyczny serwera."},
                status=500,
            )
