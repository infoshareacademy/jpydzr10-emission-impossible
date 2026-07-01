from django.urls import path

from . import views

app_name = "calculator"

urlpatterns = [
    path("converters/", views.ConvertersDashboardView.as_view(), name="dashboard"),
    path("fuel-types/add/", views.FuelTypeCreateView.as_view(), name="fueltype_add"),
    path("suppliers/add/", views.SupplierCreateView.as_view(), name="supplier_add"),
    path("fuel-specs/add/", views.FuelSpecCreateView.as_view(), name="fuelspec_add"),
    path("fuel-specs/", views.ConvertersDashboardView.as_view(), name="fuelspec_list"),
    path("suppliers/", views.ConvertersDashboardView.as_view(), name="supplier_list"),
    path("fuel-types/", views.ConvertersDashboardView.as_view(), name="fueltype_list"),
]
