from companies.models import Companies
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    EnergyConsumptionForm,
    EnergyProducedForm,
    EnergyPurchasedForm,
    EnergySoldForm,
    FugitiveEmissionForm,
    MobileCombustionForm,
    ProcessEmissionForm,
    StationaryCombustionForm,
)
from .models import (
    EnergyConsumption,
    EnergyProduced,
    EnergyPurchased,
    EnergySold,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)


def energy_consumption_list(request):
    """Wyświetla listę rekordów zużycia energii z możliwością filtrowania."""
    records = EnergyConsumption.objects.all().order_by("-year", "company")
    company = request.GET.get("company", "").strip()
    year_str = request.GET.get("year", "").strip()

    if company:
        records = records.filter(company__icontains=company)

    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    context = {
        "records": page_obj,
        "page_obj": page_obj,
        "page_range": elided_page_range,
        "title": "Zużycie energii",
        "filter_company": company,
        "filter_year": year_str,
    }
    return render(request, "emissions/energy_consumption_list.html", context)


# @login_required
def energy_consumption_add(request):
    """Formularz dodawania nowego rekordu zużycia energii."""
    if request.method == "POST":
        form = EnergyConsumptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord zużycia energii został dodany.")
            return redirect("energy_consumption_list")
    else:
        form = EnergyConsumptionForm()

    return render(
        request,
        "emissions/energy_consumption_form.html",
        {"form": form, "title": "Dodaj zużycie energii"},
    )


# @login_required
def energy_consumption_edit(request, pk):
    """Formularz edycji istniejącego rekordu zużycia energii."""
    record = get_object_or_404(EnergyConsumption, pk=pk)

    if request.method == "POST":
        form = EnergyConsumptionForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord został zaktualizowany.")
            return redirect("energy_consumption_list")
    else:
        form = EnergyConsumptionForm(instance=record)

    return render(
        request,
        "emissions/energy_consumption_form.html",
        {"form": form, "title": "Edytuj zużycie energii"},
    )


# @login_required
def energy_consumption_delete(request, pk):
    """Usuwa rekord zużycia energii po potwierdzeniu."""
    record = get_object_or_404(EnergyConsumption, pk=pk)

    if request.method == "POST":
        record.delete()
        messages.success(request, "Rekord został usunięty.")
        return redirect("energy_consumption_list")

    return render(
        request,
        "emissions/energy_consumption_confirm_delete.html",
        {"record": record, "title": "Potwierdź usunięcie"},
    )


def energy_purchased_list(request):
    """Wyświetla listę rekordów zakupionej energii z filtrowaniem i paginacją."""
    records = EnergyPurchased.objects.all().order_by("-year", "company")
    company = request.GET.get("company", "").strip()
    year_str = request.GET.get("year", "").strip()

    if company:
        records = records.filter(company__icontains=company)
    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    elided_page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    context = {
        "records": page_obj,
        "page_obj": page_obj,
        "page_range": elided_page_range,
        "title": "Zakupiona energia",
        "filter_company": company,
        "filter_year": year_str,
    }
    return render(request, "emissions/energy_purchased_list.html", context)


# @login_required
def energy_purchased_add(request):
    if request.method == "POST":
        form = EnergyPurchasedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord zakupionej energii został dodany.")
            return redirect("energy_purchased_list")
    else:
        form = EnergyPurchasedForm()
    return render(
        request,
        "emissions/energy_purchased_form.html",
        {"form": form, "title": "Dodaj zakupioną energię"},
    )


# @login_required
def energy_purchased_edit(request, pk):
    record = get_object_or_404(EnergyPurchased, pk=pk)
    if request.method == "POST":
        form = EnergyPurchasedForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord został zaktualizowany.")
            return redirect("energy_purchased_list")
    else:
        form = EnergyPurchasedForm(instance=record)
    return render(
        request,
        "emissions/energy_purchased_form.html",
        {"form": form, "title": "Edytuj zakupioną energię"},
    )


# @login_required
def energy_purchased_delete(request, pk):
    record = get_object_or_404(EnergyPurchased, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Rekord został usunięty.")
        return redirect("energy_purchased_list")
    return render(
        request,
        "emissions/energy_purchased_confirm_delete.html",
        {"record": record, "title": "Potwierdź usunięcie"},
    )


def energy_produced_list(request):
    """Wyświetla listę rekordów wyprodukowanej energii."""
    records = EnergyProduced.objects.all().order_by("-year", "company")
    company = request.GET.get("company", "").strip()
    year_str = request.GET.get("year", "").strip()

    if company:
        records = records.filter(company__icontains=company)
    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    context = {
        "records": page_obj,
        "page_obj": page_obj,
        "page_range": elided_page_range,
        "title": "Wyprodukowana energia",
        "filter_company": company,
        "filter_year": year_str,
    }
    return render(request, "emissions/energy_produced_list.html", context)


# @login_required
def energy_produced_add(request):
    if request.method == "POST":
        form = EnergyProducedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord wyprodukowanej energii został dodany.")
            return redirect("energy_produced_list")
    else:
        form = EnergyProducedForm()
    return render(
        request,
        "emissions/energy_produced_form.html",
        {"form": form, "title": "Dodaj wyprodukowaną energię"},
    )


# @login_required
def energy_produced_edit(request, pk):
    record = get_object_or_404(EnergyProduced, pk=pk)
    if request.method == "POST":
        form = EnergyProducedForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Rekord został zaktualizowany.")
            return redirect("energy_produced_list")
    else:
        form = EnergyProducedForm(instance=record)
    return render(
        request,
        "emissions/energy_produced_form.html",
        {"form": form, "title": "Edytuj wyprodukowaną energię"},
    )


# @login_required
def energy_produced_delete(request, pk):
    record = get_object_or_404(EnergyProduced, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Rekord został usunięty.")
        return redirect("energy_produced_list")
    return render(
        request,
        "emissions/energy_produced_confirm_delete.html",
        {"record": record, "title": "Potwierdź usunięcie"},
    )


def energy_sold_list(request):
    """Wyświetla listę rekordów sprzedanej energii."""
    records = EnergySold.objects.all().order_by("-year", "company")
    company = request.GET.get("company", "").strip()
    year_str = request.GET.get("year", "").strip()

    if company:
        records = records.filter(company__icontains=company)
    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    context = {
        "records": page_obj,
        "page_obj": page_obj,
        "page_range": elided_page_range,
        "title": _("Sprzedana energia"),
        "filter_company": company,
        "filter_year": year_str,
    }
    return render(request, "emissions/energy_sold_list.html", context)


# @login_required
def energy_sold_add(request):
    if request.method == "POST":
        form = EnergySoldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Rekord sprzedanej energii został dodany."))
            return redirect("energy_sold_list")
    else:
        form = EnergySoldForm()
    return render(
        request,
        "emissions/energy_sold_form.html",
        {"form": form, "title": _("Dodaj sprzedaną energię")},
    )


# @login_required
def energy_sold_edit(request, pk):
    record = get_object_or_404(EnergySold, pk=pk)
    if request.method == "POST":
        form = EnergySoldForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, _("Rekord został zaktualizowany."))
            return redirect("energy_sold_list")
    else:
        form = EnergySoldForm(instance=record)
    return render(
        request,
        "emissions/energy_sold_form.html",
        {"form": form, "title": _("Edytuj sprzedaną energię")},
    )


# @login_required
def energy_sold_delete(request, pk):
    record = get_object_or_404(EnergySold, pk=pk)
    if request.method == "POST":
        record.delete()
        messages.success(request, _("Rekord został usunięty."))
        return redirect("energy_sold_list")
    return render(
        request,
        "emissions/energy_sold_confirm_delete.html",
        {"record": record, "title": _("Potwierdź usunięcie")},
    )


class Scope1CreateMixin(LoginRequiredMixin):
    """
    Wspólna logika dla wszystkich widoków dodawania z Zakresu 1.
    Używa tego samego szablonu formularza i wraca na dashboard.
    """

    template_name = (
        "emissions/scope1_form.html"  # Jeden uniwersalny szablon dla formularzy
    )
    success_url = reverse_lazy("emissions:dashboard", kwargs={"company_id": 1})

    def form_valid(self, form):
        messages.success(
            self.request, f"Pomyślnie dodano wpis do: {self.model._meta.verbose_name}"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_verbose_name"] = self.model._meta.verbose_name
        context["company_id"] = self.kwargs.get("company_id")
        return context


class StationaryCombustionListView(LoginRequiredMixin, ListView):
    model = StationaryCombustion
    template_name = "emissions/stationary_list.html"
    context_object_name = "records"


class StationaryCombustionCreateView(Scope1CreateMixin, CreateView):
    model = StationaryCombustion
    form_class = StationaryCombustionForm


class StationaryCombustionUpdateView(Scope1CreateMixin, UpdateView):
    model = StationaryCombustion

    def form_valid(self, form):
        messages.success(self.request, "Pomyślnie zaktualizowano wpis.")
        return super().form_valid(form)


class MobileCombustionCreateView(Scope1CreateMixin, CreateView):
    model = MobileCombustion
    form_class = MobileCombustionForm


class ProcessEmissionCreateView(Scope1CreateMixin, CreateView):
    model = ProcessEmission
    form_class = ProcessEmissionForm


class FugitiveEmissionCreateView(Scope1CreateMixin, CreateView):
    model = FugitiveEmission
    form_class = FugitiveEmissionForm


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Główny widok nawigacyjny kalkulatora emisji (Dashboard).
    Służy jako menu wyboru zakresów i kategorii.
    """

    template_name = "emissions/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get("company_id")
        company = get_object_or_404(Companies, pk=company_id)
        context["company"] = company

        return context
