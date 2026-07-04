from django.core.exceptions import PermissionDenied

from .models import CompanyReportEnvelope, ReportingPeriod


class ReportLockMixin:
    """
    Mixin chroniący widoki (Create, Update, Delete) przed modyfikacją danych,
    jeśli raporty dla danej spółki ma status IN_REVIEW lub APPROVED.
    Odrzuca żądanie natychmiastowym błędem HTTP 403 Forbidden.
    """

    def dispatch(self, request, *args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            company = self._get_target_company()
            active_period = ReportingPeriod.objects.filter(is_active=True).first()

            if company and active_period:
                envelope = CompanyReportEnvelope.objects.filter(
                    company=company, period=active_period
                ).first()

                if envelope and envelope.status in [
                    CompanyReportEnvelope.Status.IN_REVIEW,
                    CompanyReportEnvelope.Status.APPROVED,
                ]:
                    raise PermissionDenied(
                        "Edycja jest zablokowana. Raport dla tej spółki został "
                        "przekazany do weryfikacji lub jest już zatwierdzony."
                    )

        return super().dispatch(request, *args, **kwargs)

    def _get_target_company(self):
        if hasattr(self, "get_object"):
            try:
                obj = self.get_object()
                if hasattr(obj, "company"):
                    return obj.company
            except Exception:
                pass

        if self.request.method == "POST" and "company" in self.request.POST:
            from companies.models import Companies

            return Companies.objects.filter(id=self.request.POST.get("company")).first()

        return None
