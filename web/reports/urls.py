from django.urls import path

from . import views

app_name = "reports"
urlpatterns = [
    path("", views.GHGReportView.as_view(), name="ghg-report"),
]
