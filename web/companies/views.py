from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView

from companies.forms import CompaniesForm
from companies.models import Companies
from accounts.models import CustomUser

class CompanyAccessMixin:
    """
    Mixin filtrujący firmy na podstawie uprawnień zalogowanego użytkownika.
    """
    required_permission = 'read'

    def get_queryset(self):
        user: CustomUser = self.request.user

        if user.role == 'admin' or user.is_superuser:
            return Companies.objects.all()

        if self.required_permission == 'save':
            return Companies.objects.filter(
                user_permissions__user=user,
                user_permissions__can_save=True
            ).distinct()
        else:
            return Companies.objects.filter(
                user_permissions__user=user,
                user_permissions__can_read=True
            ).distinct()


class CompaniesListView(CompanyAccessMixin, ListView):
    model = Companies
    template_name = 'companies/companies_list.html'
    context_object_name = 'companies'

class CompaniesDetailView(CompanyAccessMixin, DetailView):
    model = Companies
    template_name = 'companies/companies_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'company'

class CompaniesCreateView(LoginRequiredMixin, CreateView):
    model = Companies
    form_class = CompaniesForm
    template_name = 'companies/companies_detail.html'
    required_permission = 'save'
    success_url = '/companies/'

    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     form.instance.updated_by = self.request.user
    #     return super().form_valid(form)