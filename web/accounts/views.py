from companies.models import Companies
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView, View

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


User = get_user_model()


def _is_admin(user) -> bool:
    return user.is_superuser or getattr(user, "role", "") == "admin"


class CompanyUsersListView(LoginRequiredMixin, TemplateView):
    """
    Widok listy użytkowników pogrupowanych według spółek.

    Admin widzi wszystko i może zarządzać użytkownikami.
    Zwykły użytkownik/audytor widzi tylko spółki, do których ma dostęp.
    """

    template_name = "accounts/company_users_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_admin = _is_admin(user)

        admins = (
            User.objects.filter(Q(role="admin") | Q(is_superuser=True))
            .distinct()
            .order_by("username")
        )

        if is_admin:
            companies = Companies.objects.all().order_by("name")
        else:
            companies = (
                Companies.objects.filter(
                    user_permissions__user=user,
                    user_permissions__can_read=True,
                )
                .distinct()
                .order_by("name")
            )

        # ── Dane per spółka ───────────────────────────────────────────────
        company_data = []
        for company in companies:
            perms = (
                UserCompanyPermission.objects.filter(company=company)
                .exclude(user__role="admin")
                .exclude(user__is_superuser=True)
                .select_related("user")
                .order_by("user__username")
            )
            company_data.append(
                {
                    "company": company,
                    "permissions": list(perms),
                    "user_count": perms.count(),
                }
            )

        if is_admin:
            total_users = User.objects.filter(is_active=True).count()
            total_all_users = User.objects.count()
        else:
            total_users = (
                UserCompanyPermission.objects.filter(company__in=companies)
                .values("user")
                .distinct()
                .count()
            )
            total_all_users = total_users

        context.update(
            {
                "admins": admins,
                "company_data": company_data,
                "is_admin": is_admin,
                "total_companies": companies.count(),
                "total_users": total_users,
                "total_all_users": total_all_users,
                "admin_count": admins.count(),
            }
        )
        return context


class RemoveUserFromCompanyView(LoginRequiredMixin, View):
    """Usuwa powiązanie UserCompanyPermission — tylko admin."""

    def post(self, request, pk: int):
        if not _is_admin(request.user):
            messages.error(request, "Brak uprawnień do wykonania tej operacji.")
            return redirect("accounts:company-users-list")

        perm = get_object_or_404(UserCompanyPermission, pk=pk)
        username = perm.user.username
        company_name = perm.company.name
        perm.delete()

        messages.success(
            request,
            f"Użytkownik '{username}' został odpięty od spółki '{company_name}'.",
        )
        return redirect("accounts:company-users-list")


class DeactivateUserView(LoginRequiredMixin, View):
    """Dezaktywuje konto użytkownika (is_active=False) — tylko admin."""

    def post(self, request, pk: int):
        if not _is_admin(request.user):
            messages.error(request, "Brak uprawnień do wykonania tej operacji.")
            return redirect("accounts:company-users-list")

        target_user = get_object_or_404(User, pk=pk)

        if target_user == request.user:
            messages.error(request, "Nie możesz dezaktywować własnego konta.")
            return redirect("accounts:company-users-list")

        if _is_admin(target_user):
            messages.error(
                request,
                f"Nie można dezaktywować konta administratora '{target_user.username}'.",
            )
            return redirect("accounts:company-users-list")

        target_user.is_active = False
        target_user.save(update_fields=["is_active"])

        messages.success(
            request,
            f"Konto użytkownika '{target_user.username}' zostało dezaktywowane.",
        )
        return redirect("accounts:company-users-list")
