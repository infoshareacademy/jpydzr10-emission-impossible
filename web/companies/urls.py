from django.urls import path
from . import views

app_name = "companies"
urlpatterns = [
    path("", views.CompaniesListView.as_view(), name='companies-list'),
    path("<int:pk>/", views.CompaniesDetailView.as_view(), name='companies-detail'),
    path("create/", views.CompaniesCreateView.as_view(), name='companies-create'),
]