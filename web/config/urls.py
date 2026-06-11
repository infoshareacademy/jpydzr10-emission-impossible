from core.views import HomeView
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("companies/", include("companies.urls")),
    path("emissions/", include("emissions.urls")),
    path("reports/", include("reports.urls")),
    path("what_if/", include("what_if.urls")),
]
