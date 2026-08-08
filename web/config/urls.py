from core.views import HomeView, PrivacyPolicyView
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path("", HomeView.as_view(), name="home"),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("companies/", include("companies.urls")),
    path("emissions/", include("emissions.urls")),
    path("reports/", include("reports.urls")),
    path("what_if/", include("what_if.urls")),
    path("ai/", include("ai_services.urls")),
    path("calculator/", include("calculator.urls")),
    path("communications/", include("communications.urls")),
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
    path("workflow/", include("workflow.urls", namespace="workflow")),
    path('audit/', include('audit.urls', namespace='audit')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
