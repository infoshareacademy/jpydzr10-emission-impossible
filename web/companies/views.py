import datetime

from accounts.models import CustomUser
from core.mixins import PageViewTrackerMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from emissions.models import (
    EnergyConsumption,
    EnergyProduced,
    EnergyPurchased,
    EnergySold,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)

from companies.forms import CompaniesForm
from companies.models import Companies


class CompanyAccessMixin:
    """
    Mixin filtrujący firmy na podstawie uprawnień zalogowanego użytkownika.
    """

    required_permission = "read"

    def get_queryset(self):
        user: CustomUser = self.request.user

        if user.role == "admin" or user.is_superuser:
            return Companies.objects.all()

        if self.required_permission == "save":
            return Companies.objects.filter(
                user_permissions__user=user, user_permissions__can_save=True
            ).distinct()
        else:
            return Companies.objects.filter(
                user_permissions__user=user, user_permissions__can_read=True
            ).distinct()


class CompaniesListView(PageViewTrackerMixin, CompanyAccessMixin, ListView):
    model = Companies
    template_name = "companies/companies_list.html"
    context_object_name = "companies"
    tracked_view_name = "Lista Firm"

    def _get_selected_year(self):
        """Metoda pomocnicza do ujednolicenia pobierania roku z requestu (DRY)"""
        current_year = timezone.now().year
        try:
            return int(self.request.GET.get("year", current_year))
        except ValueError:
            return current_year
        
    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(nip__icontains=query))

        try:
            selected_year = int(
                self.request.GET.get("year", datetime.datetime.now().year)
            )
        except ValueError:
            selected_year = datetime.datetime.now().year

        qs = qs.annotate(
            has_stationary=Exists(
                StationaryCombustion.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_mobile=Exists(
                MobileCombustion.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_process=Exists(
                ProcessEmission.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_fugitive=Exists(
                FugitiveEmission.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_e_cons=Exists(
                EnergyConsumption.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_e_purc=Exists(
                EnergyPurchased.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_e_prod=Exists(
                EnergyProduced.objects.filter(
                    company=OuterRef("pk"), year=selected_year
                )
            ),
            has_e_sold=Exists(
                EnergySold.objects.filter(company=OuterRef("pk"), year=selected_year)
            ),
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_year = self._get_selected_year()
        context["selected_year"] = selected_year

        current_year = timezone.now().year
        context["available_years"] = range(2019, current_year + 3)

        for company in context["companies"]:
            filled_tables = sum(
                [
                    company.has_stationary,
                    company.has_mobile,
                    company.has_process,
                    company.has_fugitive,
                    company.has_e_cons,
                    company.has_e_purc,
                    company.has_e_prod,
                    company.has_e_sold,
                ]
            )
            company.completion_percentage = int((filled_tables / 8) * 100)

        return context


class CompaniesDetailView(CompanyAccessMixin, DetailView):
    model = Companies
    template_name = "companies/companies_detail.html"
    pk_url_kwarg = "pk"
    context_object_name = "company"


class CompaniesCreateView(LoginRequiredMixin, CreateView):
    model = Companies
    form_class = CompaniesForm
    template_name = "companies/companies_form.html"
    required_permission = "save"
    success_url = reverse_lazy("companies:companies-list")

    def form_valid(self, form):
        messages.success(self.request, "Pomyślnie dodano nową spółkę.")
        return super().form_valid(form)


class CompaniesUpdateView(LoginRequiredMixin, UpdateView):
    model = Companies
    pk_url_kwarg = "pk"
    form_class = CompaniesForm
    template_name = "companies/companies_detail.html"
    required_permission = "save"
    success_url = reverse_lazy("companies:companies-list")

    def form_valid(self, form):
        messages.success(self.request, "Zmiany zostały zapisane.")
        return super().form_valid(form)


class CompaniesDeleteView(LoginRequiredMixin, DeleteView):
    model = Companies
    pk_url_kwarg = "pk"
    form_class = CompaniesForm
    template_name = "companies/companies_detail.html"
