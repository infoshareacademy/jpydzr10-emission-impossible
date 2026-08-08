import json
from decimal import Decimal

from companies.models import Companies
from core.mixins import PageViewTrackerMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from emissions.models import (
    EmissionFactor,
    EnergyConsumption,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)

from .forms import ReductionTargetForm, SimulationForm
from .models import ReductionGoal, ReductionTarget


class ReductionTargetListView(PageViewTrackerMixin, LoginRequiredMixin, ListView):
    """Widok listy celów redukcyjnych z wbudowanym filtrem wyboru spółki."""

    model = ReductionTarget
    template_name = "what_if/reduction_target_list.html"
    paginate_by = 15
    context_object_name = "targets"

    def get_allowed_companies(self):
        user = self.request.user
        if user.role == "admin" or user.is_superuser:
            return Companies.objects.all().order_by("name")
        return (
            Companies.objects.filter(
                user_permissions__user=user, user_permissions__can_read=True
            )
            .distinct()
            .order_by("name")
        )

    def get(self, request, *args, **kwargs):
        chosen_company_id = request.GET.get("company_id")
        if chosen_company_id:
            request.session["active_company_id"] = chosen_company_id
            return HttpResponseRedirect(reverse_lazy("what_if:reduction-target-list"))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return ReductionTarget.objects.none()

        allowed_companies = self.get_allowed_companies()
        self.company = get_object_or_404(allowed_companies, pk=company_id)

        # Zabezpieczenie przed N+1 przez dołączenie relacji 'goal' i 'company'
        return (
            ReductionTarget.objects.filter(company=self.company)
            .select_related("company", "goal")
            .order_by("goal__target_year")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allowed_companies"] = self.get_allowed_companies()
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["active_company_id"] = int(company_id)
            context["company"] = Companies.objects.filter(pk=company_id).first()

        context["add_url_name"] = "what_if:reduction-target-add"
        context["edit_url_name"] = "what_if:reduction-target-edit"
        context["delete_url_name"] = "what_if:reduction-target-delete"
        return context


class ReductionTargetMixin(LoginRequiredMixin):
    model = ReductionTarget
    form_class = ReductionTargetForm
    template_name = "what_if/reduction_target_form.html"

    def get_form_kwargs(self):
        """Wstrzykuje aktywną spółkę do formularza, aby przefiltrować listę celów."""
        kwargs = super().get_form_kwargs()
        kwargs["company"] = getattr(self, "company", None)
        return kwargs

    def get_success_url(self):
        return reverse_lazy("what_if:reduction-target-list")

    def get_active_company(self):
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            messages.error(self.request, "Wybierz najpierw spółkę z listy celów.")
            return None

        user = self.request.user
        if user.role == "admin" or user.is_superuser:
            return get_object_or_404(Companies, pk=company_id)

        return get_object_or_404(
            Companies,
            pk=company_id,
            user_permissions__user=user,
            user_permissions__can_read=True,
        )

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_active_company()
        if not self.company:
            return HttpResponseRedirect(reverse_lazy("what_if:reduction-target-list"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.company = self.company

        if (
            ReductionTarget.objects.filter(company=self.company, goal=instance.goal)
            .exclude(pk=instance.pk)
            .exists()
        ):
            form.add_error("goal", "Ten cel został już przypisany do wybranej spółki.")
            return self.form_invalid(form)

        is_new = instance.pk is None
        instance.save()

        action_text = "przypisano" if is_new else "zaktualizowano przypisanie"
        messages.success(
            self.request,
            f"Pomyślnie {action_text} cel redukcyjny: {instance.goal.name} dla {self.company.name}",
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.company
        context["list_url_name"] = "what_if:reduction-target-list"
        return context


class ReductionTargetCreateView(ReductionTargetMixin, CreateView):
    pass


class ReductionTargetUpdateView(ReductionTargetMixin, UpdateView):
    pass


class ReductionTargetDeleteView(LoginRequiredMixin, DeleteView):
    model = ReductionTarget
    template_name = "what_if/reduction_target_confirm_delete.html"
    success_url = reverse_lazy("what_if:reduction-target-list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Pomyślnie usunięto cel redukcyjny.")
        return super().delete(request, *args, **kwargs)


class SimulationDashboardView(LoginRequiredMixin, FormView):
    template_name = "what_if/simulation.html"
    form_class = SimulationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        if self.request.GET:
            kwargs["data"] = self.request.GET
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()

        factors_dict = {
            str(f.id): float(f.factor) for f in EmissionFactor.objects.all()
        }
        context["factors_json"] = json.dumps(factors_dict)

        actual_emissions = {
            "scope_1": Decimal("0.0"),
            "scope_2": Decimal("0.0"),
            "total": Decimal("0.0"),
            "sources": {},
        }
        simulated_emissions = None

        if form.is_valid():
            company = form.cleaned_data.get("company")
            current_factor = form.cleaned_data.get("current_factor")
            reduced_amount = form.cleaned_data.get("reduced_amount")
            new_factor = form.cleaned_data.get("new_factor")
            added_amount = form.cleaned_data.get("added_amount")

            qs_filters = {"company": company} if company else {}

            mob_sum = MobileCombustion.objects.filter(**qs_filters).aggregate(
                total=Sum("emission_tco2eq")
            )["total"] or Decimal("0.0")
            stat_sum = StationaryCombustion.objects.filter(**qs_filters).aggregate(
                total=Sum("emission_tco2eq")
            )["total"] or Decimal("0.0")
            proc_sum = ProcessEmission.objects.filter(**qs_filters).aggregate(
                total=Sum("emission_tco2eq")
            )["total"] or Decimal("0.0")
            fug_sum = FugitiveEmission.objects.filter(**qs_filters).aggregate(
                total=Sum("emission_tco2eq")
            )["total"] or Decimal("0.0")

            actual_emissions["scope_1"] = mob_sum + stat_sum + proc_sum + fug_sum
            actual_emissions["sources"]["Zakres 1 (Emisje bezpośrednie)"] = (
                actual_emissions["scope_1"]
            )

            e_sum = EnergyConsumption.objects.filter(**qs_filters).aggregate(
                total=Sum("emission_tco2eq")
            )["total"] or Decimal("0.0")
            actual_emissions["scope_2"] = e_sum
            actual_emissions["sources"]["Zakres 2 (Emisje pośrednie)"] = (
                actual_emissions["scope_2"]
            )

            actual_emissions["total"] = (
                actual_emissions["scope_1"] + actual_emissions["scope_2"]
            )

            emission_reduced = reduced_amount * current_factor.factor
            emission_added = added_amount * new_factor.factor

            simulated_emission_change = emission_added - emission_reduced
            simulated_total = actual_emissions["total"] + simulated_emission_change

            simulated_emissions = {
                "total": max(Decimal("0.0"), simulated_total),
                "difference": simulated_emission_change,
                "emission_reduced": emission_reduced,
                "emission_added": emission_added,
                "current_factor_name": current_factor.factor_name,
                "new_factor_name": new_factor.factor_name,
            }
            context["simulated"] = simulated_emissions

        context["actual"] = actual_emissions
        return context


class ReductionTargetDetailView(LoginRequiredMixin, DetailView):
    model = ReductionTarget
    template_name = "what_if/reduction_target_detail.html"
    context_object_name = "target"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target = self.object

        years = list(range(target.base_year, target.target_year + 1))
        qs_filters = {"company": target.company, "year__in": years}

        def get_yearly_totals(model_class):
            qs = (
                model_class.objects.filter(**qs_filters)
                .values("year")
                .annotate(t=Sum("emission_tco2eq"))
            )
            return {item["year"]: item["t"] or Decimal("0.0") for item in qs}

        mob_totals = (
            get_yearly_totals(MobileCombustion)
            if target.scope in ["Scope 1", "1+2"]
            else {}
        )
        stat_totals = (
            get_yearly_totals(StationaryCombustion)
            if target.scope in ["Scope 1", "1+2"]
            else {}
        )
        proc_totals = (
            get_yearly_totals(ProcessEmission)
            if target.scope in ["Scope 1", "1+2"]
            else {}
        )
        fug_totals = (
            get_yearly_totals(FugitiveEmission)
            if target.scope in ["Scope 1", "1+2"]
            else {}
        )
        e_totals = (
            get_yearly_totals(EnergyConsumption)
            if target.scope in ["Scope 2", "1+2"]
            else {}
        )

        actual_emissions_by_year = []

        for y in years:
            total_y = Decimal("0.0")

            if target.scope in ["Scope 1", "1+2"]:
                total_y += mob_totals.get(y, Decimal("0.0"))
                total_y += stat_totals.get(y, Decimal("0.0"))
                total_y += proc_totals.get(y, Decimal("0.0"))
                total_y += fug_totals.get(y, Decimal("0.0"))

            if target.scope in ["Scope 2", "1+2"]:
                total_y += e_totals.get(y, Decimal("0.0"))

            actual_emissions_by_year.append(float(total_y))

        base_emission = actual_emissions_by_year[0] if actual_emissions_by_year else 0.0
        target_emission = base_emission * (1 - (float(target.reduction_pct) / 100))

        context["chart_years"] = years
        context["chart_actual"] = actual_emissions_by_year
        context["chart_target_line"] = [
            (
                base_emission
                - (((base_emission - target_emission) / (len(years) - 1)) * i)
                if len(years) > 1
                else base_emission
            )
            for i in range(len(years))
        ]

        context["base_emission_value"] = base_emission
        context["target_emission_value"] = target_emission

        return context

class AdminRequiredMixin(UserPassesTestMixin):
    """Zabezpieczenie: tylko admin/superuser ma dostęp do globalnych celów."""
    def test_func(self):
        return self.request.user.is_superuser or getattr(self.request.user, 'role', '') == 'admin'

class ReductionGoalListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ReductionGoal
    template_name = "what_if/goal_list.html"
    context_object_name = "goals"

class ReductionGoalCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ReductionGoal
    template_name = "what_if/goal_form.html"
    fields = ['company', 'name', 'base_year', 'target_year', 'reduction_pct', 'scope']
    success_url = reverse_lazy('what_if:goal_list')

    def form_valid(self, form):
        messages.success(self.request, "Pomyślnie utworzono nowy cel redukcyjny.")
        return super().form_valid(form)

class ReductionGoalUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ReductionGoal
    template_name = "what_if/goal_form.html"  # Używa tego samego, udostępnionego wcześniej szablonu!
    fields = ["company", "name", "base_year", "target_year", "reduction_pct", "scope"]
    success_url = reverse_lazy("what_if:goal_list")

    def form_valid(self, form):
        messages.success(self.request, "Cel redukcyjny został zaktualizowany.")
        return super().form_valid(form)


class ReductionGoalDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = ReductionGoal
    success_url = reverse_lazy("what_if:goal_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cel redukcyjny został pomyślnie usunięty.")
        return super().delete(request, *args, **kwargs)