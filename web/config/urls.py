from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("companies/", include("companies.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("emissions/", include("emissions.urls")),
]
