from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    # Wbudowane widoki resetu hasła
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
]
