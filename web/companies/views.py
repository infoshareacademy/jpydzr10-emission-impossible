from accounts.models import CustomUser
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
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


class CompaniesListView(CompanyAccessMixin, ListView):
    model = Companies
    template_name = "companies/companies_list.html"
    context_object_name = "companies"


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
