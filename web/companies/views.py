from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from companies.models import Companies
from accounts.models import CustomUser


class CompaniesListView(ListView):
    model = Companies
    template_name = 'companies/companies_list.html'
    context_object_name = 'companies'

    def get_queryset(self):
        user: CustomUser = self.request.user

        if user.role == 'admin' or user.is_superuser:
            return Companies.objects.all()
        else:
            return Companies.objects.filter(
                user_permissions__user = self.request.user,
                user_permissions__can_read = True
            )

    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     form.instance.updated_by = self.request.user
    #     return super().form_valid(form)