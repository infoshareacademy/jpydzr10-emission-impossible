from django.urls import path
from . import views

app_name = "companies"
urlpatterns = [
    path("", views.CompaniesListView.as_view(), name='companies-list'),
    path("detail/<int:pk>/", views.CompaniesDetailView.as_view(), name='companies-detail'),
    path("create/", views.CompaniesCreateView.as_view(), name='companies-create'),
    path("update/<int:pk>/", views.CompaniesUpdateView.as_view(), name='companies-update'),
    path("delete/<int:pk>/", views.CompaniesDeleteView.as_view(), name='companies-delete'),
]