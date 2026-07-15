import re

from companies.models import Companies
from django.core.exceptions import PermissionDenied

from .models import CompanyReportEnvelope, ReportingPeriod


class ReportLockMixin:
    """
    Mixin chroniący przed modyfikacją danych z zamkniętych okresów raportowych.
    Działa w oparciu o "Białą Listę": edycja jest możliwa TYLKO wtedy, gdy dla danej
    spółki i roku istnieje koperta (CompanyReportEnvelope) o statusie pozwalającym na edycję.
    """

    def dispatch(self, request, *args, **kwargs):
        company = self._get_target_company()
        target_year = self._get_target_year()

        if company and target_year:
            period = self._get_period_for_year(target_year)

            if period:
                envelope = CompanyReportEnvelope.objects.filter(
                    company=company, period=period
                ).first()

                if not envelope:
                    raise PermissionDenied(
                        f"Brak uprawnień. Spółka {company.name} nie została przypisana "
                        f"do okresu raportowego {target_year}. Najpierw otwórz dla niej raport."
                    )

                if envelope.status in [
                    CompanyReportEnvelope.Status.IN_REVIEW,
                    CompanyReportEnvelope.Status.APPROVED,
                ]:
                    raise PermissionDenied(
                        f"Edycja jest zablokowana. Raport dla {company.name} za rok {target_year} "
                        "został przekazany do weryfikacji lub jest już zatwierdzony."
                    )

            else:
                raise PermissionDenied(
                    f"W systemie brak zdefiniowanego okresu raportowego dla roku {target_year}."
                )

        return super().dispatch(request, *args, **kwargs)

    def _get_target_company(self):
        """Identyfikuje spółkę na podstawie URL, edytowanego obiektu lub danych POST."""
        company_id = self.kwargs.get("company_id")
        if company_id:
            return Companies.objects.filter(id=company_id).first()

        if hasattr(self, "get_object"):
            try:
                obj = getattr(self, "object", None) or self.get_object()
                if hasattr(obj, "company"):
                    return obj.company
            except Exception:
                pass

        if (
            self.request.method in ["POST", "PUT", "PATCH"]
            and "company" in self.request.POST
        ):
            return Companies.objects.filter(id=self.request.POST.get("company")).first()

        return None

    def _get_target_year(self):
        """Identyfikuje rok, którego dotyczy operacja."""
        if hasattr(self, "get_object") and "pk" in self.kwargs:
            try:
                obj = getattr(self, 'object', None) or self.get_object()
                if hasattr(obj, "year"):
                    return obj.year
            except Exception:
                pass

        if self.request.method in ["POST", "PUT", "PATCH"] and "year" in self.request.POST:
            return self.request.POST.get("year")

        if self.request.method == "GET" and "year" in self.request.GET:
            return self.request.GET.get("year")

        return None

    def _get_period_for_year(self, year):
        """
        Dopasowuje rok (np. 2025) do konkretnego obiektu ReportingPeriod w bazie.
        """
        return ReportingPeriod.objects.filter(year=year).first()

    def _extract_year_from_period(self, period):
        """Pomocnicza metoda wyciągająca rocznik (np. '2026') z obiektu okresu."""
        if hasattr(period, "year") and getattr(period, "year"):
            return period.year

        match = re.search(r"\d{4}", str(period))
        return match.group() if match else None
