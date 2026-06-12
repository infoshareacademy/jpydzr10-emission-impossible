from companies.models import Companies
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ReductionTargetForm
from .models import ReductionTarget


class ReductionTargetListView(LoginRequiredMixin, ListView):
    """Widok listy celów redukcyjnych z wbudowanym filtrem wyboru spółki."""

    model = ReductionTarget
    template_name = "what_if/reduction_target_list.html"
    paginate_by = 15
    context_object_name = "targets"

    def get_allowed_companies(self):
        """Pomocnicza metoda zwracająca spółki, do których zalogowany użytkownik ma dostęp."""
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
        # Sprawdzamy, czy użytkownik zmienił spółkę za pomocą formularza (parametr GET ?company_id=...)
        chosen_company_id = request.GET.get("company_id")

        if chosen_company_id:
            # Zapisujemy wybraną firmę w sesji użytkownika
            request.session["active_company_id"] = chosen_company_id
            return HttpResponseRedirect(reverse_lazy("what_if:reduction-target-list"))

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Pobieramy aktywną firmę z sesji
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return (
                ReductionTarget.objects.none()
            )  # Jeśli brak wybranej firmy, nie pokazujemy żadnych rekordów

        # Bezpieczeństwo: upewniamy się, że użytkownik ma prawo do tej konkretnej firmy
        allowed_companies = self.get_allowed_companies()
        self.company = get_object_or_404(allowed_companies, pk=company_id)

        return ReductionTarget.objects.filter(company=self.company).order_by(
            "target_year"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Przekazujemy listę do selecta
        context["allowed_companies"] = self.get_allowed_companies()

        # Przekazujemy aktualnie wybraną firmę (jeśli istnieje)
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["active_company_id"] = int(company_id)
            context["company"] = Companies.objects.filter(pk=company_id).first()

        context["add_url_name"] = "what_if:reduction-target-add"
        context["edit_url_name"] = "what_if:reduction-target-edit"
        context["delete_url_name"] = "what_if:reduction-target-delete"
        return context


class ReductionTargetMixin(LoginRequiredMixin):
    """Wspólna logika dla widoków CUD działająca w oparciu o aktywną spółkę z sesji."""

    model = ReductionTarget
    form_class = ReductionTargetForm
    template_name = "what_if/reduction_target_form.html"

    def get_success_url(self):
        return reverse_lazy("what_if:reduction-target-list")

    def get_active_company(self):
        """Pobiera i waliduje spółkę zapisaną w sesji użytkownika."""
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            messages.error(self.request, "Wybierz najpierw spółkę z listy celów.")
            return None

        # Filtrujemy po uprawnieniach użytkownika dla bezpieczeństwa
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
        instance.company = self.company  # Przypisujemy firmę wyciągniętą z sesji

        is_new = instance.pk is None
        instance.save()

        action_text = "dodano nowy" if is_new else "zaktualizowano"
        messages.success(
            self.request,
            f"Pomyślnie {action_text} cel redukcyjny: {instance.target_name} dla {self.company.name}",
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
