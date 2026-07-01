from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView

from .forms import FuelSpecForm, FuelTypeForm, SupplierForm
from .models import FuelSpec, FuelType, Supplier


class FuelTypeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = FuelType
    form_class = FuelTypeForm
    template_name = (
        "calculator/fueltype_form.html"  # Ścieżkę dostosuj do swojej struktury
    )
    success_message = "Typ paliwa '%(name)s' został pomyślnie dodany."
    # Po udanym zapisie przekieruj (np. na listę paliw lub z powrotem do formularza)
    success_url = reverse_lazy("calculator:dashboard")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.company = getattr(self.request.user, "company", None)
        return super().form_valid(form)


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "calculator/supplier_form.html"
    success_message = "Dostawca '%(name)s' został pomyślnie dodany."
    success_url = reverse_lazy("calculator:dashboard")


class FuelSpecCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = FuelSpec
    form_class = FuelSpecForm
    template_name = "calculator/fuelspec_form.html"
    success_message = "Specyfikacja paliwa została pomyślnie dodana."
    success_url = reverse_lazy("calculator:dashboard")


class ConvertersDashboardView(LoginRequiredMixin, TemplateView):
    """
    Główny pulpit zarządzania przelicznikami, wartościami opałowymi i dostawcami.
    """

    template_name = "calculator/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pobieramy dane uporządkowane alfabetycznie/logicznie
        context["fuel_types"] = FuelType.objects.all().order_by("name")
        context["suppliers"] = Supplier.objects.all().order_by("name")
        # select_related zoptymalizuje zapytanie SQL (unikniemy problemu N+1)
        context["fuel_specs"] = (
            FuelSpec.objects.select_related("fuel_type", "supplier")
            .all()
            .order_by("fuel_type__name")
        )
        return context


class FuelSpecListView(LoginRequiredMixin, ListView):
    model = FuelSpec
    template_name = "calculator/fuelspec_list.html"
    context_object_name = "fuel_specs"