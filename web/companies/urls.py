from django.urls import path

from . import views

app_name = "companies"
urlpatterns = [
    path("", views.CompaniesListView.as_view(), name="companies-list"),
    path(
        "detail/<int:pk>/", views.CompaniesDetailView.as_view(), name="company-detail"
    ),
    path("create/", views.CompaniesCreateView.as_view(), name="company-create"),
    path(
        "update/<int:pk>/", views.CompaniesUpdateView.as_view(), name="company-update"
    ),
    path(
        "delete/<int:pk>/", views.CompaniesDeleteView.as_view(), name="company-delete"
    ),
]
