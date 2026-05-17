from django.urls import path
from . import views

app_name = "companies"
urlpatterns = [
    path("", views.CompaniesListView.as_view(), name='companies-list'),
]