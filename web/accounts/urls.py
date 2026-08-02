from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("delete/", views.DeleteAccountView.as_view(), name="account_delete"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logged_out.html"),
        name="logout",
    ),
    path(
        "users/",
        views.CompanyUsersListView.as_view(),
        name="company-users-list",
    ),
    path(
        "permisions/<int:pk>/usun/",
        views.RemoveUserFromCompanyView.as_view(),
        name="permission-remove",
    ),
    path(
        "users/<int:pk>/dezaktywuj/",
        views.DeactivateUserView.as_view(),
        name="user-deactivate",
    ),
    path("2fa/setup/", views.TwoFactorSetupView.as_view(), name="2fa-setup"),
    path("2fa/verify/", views.TwoFactorVerifyView.as_view(), name="2fa-verify"),
]
