from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from core.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('accounts/', include('accounts.urls')),
    path("admin/", admin.site.urls),
    path("companies/", include("companies.urls")),
    path("emissions/", include("emissions.urls")),
    path("reports/", include("reports.urls")),
]