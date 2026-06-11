from companies.models import Companies
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from .forms import DeleteAccountForm, UserProfileForm
from .models import UserCompanyPermission


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Sprawdzamy czy użytkownik posiada rolę administratora
        if user.role == "admin":
            context["is_admin_user"] = True
            # Admin widzi absolutnie wszystkie spółki w systemie
            context["all_companies"] = Companies.objects.all()
        else:
            context["is_admin_user"] = False
            # Zwykły użytkownik widzi tylko te, do których ma jawne uprawnienie
            context["permissions"] = UserCompanyPermission.objects.filter(
                user=user
            ).select_related("company")

        return context


class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = "accounts/account_delete_confirm.html"
    form_class = DeleteAccountForm
    success_url = reverse_lazy("accounts:login")

    def get_form_kwargs(self):
        """
        Przekazujemy aktualnego użytkownika do formularza.
        Formularz 'DeleteAccountForm' wymaga argumentu 'user' w metodzie __init__.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Akcja wykonywana tylko, gdy formularz przejdzie walidację (czyli hasło jest poprawne).
        """
        user = self.request.user
        # Najpierw wylogowujemy sesję, potem usuwamy dane z DB
        logout(self.request)
        user.delete()

        messages.success(
            self.request,
            "Konto oraz powiązane dane strukturalne zostały trwale usunięte z systemu.",
        )
        return super().form_valid(form)


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "accounts/profile_edit.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("accounts:profile")
    success_message = "Dane profilu zostały pomyślnie zaktualizowane."

    def get_object(self, queryset=None):
        """
        Domyślnie UpdateView szuka obiektu po PK w URL.
        Tutaj nadpisujemy tę metodę, aby zawsze aktualizować aktualnie zalogowanego użytkownika.
        """
        return self.request.user
