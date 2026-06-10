from companies.models import Companies
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ReductionTargetForm
from .models import ReductionTarget


class ReductionTargetMixin(LoginRequiredMixin):
    """
    Wspólna logika dla widoków tworzenia i edycji Celów Redukcyjnych.
    Przypisuje cel do konkretnej firmy na podstawie company_id w URL.
    """

    model = ReductionTarget
    form_class = ReductionTargetForm
    template_name = "what_if/reduction_target_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "what_if:reduction-target-list",
            kwargs={"company_id": self.kwargs.get("company_id")},
        )

    def form_valid(self, form):
        instance = form.save(commit=False)

        # Pobieramy obiekt firmy na podstawie ID z adresu URL
        company_obj = get_object_or_404(Companies, pk=self.kwargs.get("company_id"))

        # Przypisujemy OBIEKT firmy (klucz obcy), a nie samą nazwę tekstową!
        instance.company = company_obj

        is_new = instance.pk is None
        instance.save()

        action_text = "dodano nowy" if is_new else "zaktualizowano"
        messages.success(
            self.request,
            f"Pomyślnie {action_text} cel redukcyjny: {instance.target_name}",
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company_id"] = self.kwargs.get("company_id")
        context["company"] = get_object_or_404(
            Companies, pk=self.kwargs.get("company_id")
        )
        context["list_url_name"] = "what_if:reduction-target-list"
        return context


class ReductionTargetListView(LoginRequiredMixin, ListView):
    """Widok listy celów redukcyjnych dla danej firmy."""

    model = ReductionTarget
    template_name = "what_if/reduction_target_list.html"
    paginate_by = 15

    def get_queryset(self):
        self.company = get_object_or_404(Companies, pk=self.kwargs.get("company_id"))
        qs = self.model.objects.filter(company=self.company).order_by("target_year")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.company
        context["company_id"] = self.kwargs.get("company_id")
        context["add_url_name"] = "what_if:reduction-target-add"
        context["edit_url_name"] = "what_if:reduction-target-edit"
        context["delete_url_name"] = "what_if:reduction-target-delete"
        return context


class ReductionTargetCreateView(ReductionTargetMixin, CreateView):
    """Widok dodawania nowego celu redukcyjnego."""

    pass


class ReductionTargetUpdateView(ReductionTargetMixin, UpdateView):
    """Widok edycji istniejącego celu redukcyjnego."""

    pass


class ReductionTargetDeleteView(LoginRequiredMixin, DeleteView):
    """Widok usuwania celu redukcyjnego."""

    model = ReductionTarget
    template_name = "what_if/reduction_target_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "what_if:reduction-target-list",
            kwargs={"company_id": self.kwargs.get("company_id")},
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Pomyślnie usunięto cel redukcyjny.")
        return super().delete(request, *args, **kwargs)
