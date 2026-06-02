from django.urls import path

from . import views

app_name = "emissions"

urlpatterns = [
    path("energia/", views.energy_consumption_list, name="energy_consumption_list"),
    path("energia/dodaj/", views.energy_consumption_add, name="energy_consumption_add"),
    path(
        "energia/edytuj/<int:pk>/",
        views.energy_consumption_edit,
        name="energy_consumption_edit",
    ),
    path(
        "energia/usun/<int:pk>/",
        views.energy_consumption_delete,
        name="energy_consumption_delete",
    ),
    path(
        "energia-zakupiona/", views.energy_purchased_list, name="energy_purchased_list"
    ),
    path(
        "energia-zakupiona/dodaj/",
        views.energy_purchased_add,
        name="energy_purchased_add",
    ),
    path(
        "energia-zakupiona/edytuj/<int:pk>/",
        views.energy_purchased_edit,
        name="energy_purchased_edit",
    ),
    path(
        "energia-zakupiona/usun/<int:pk>/",
        views.energy_purchased_delete,
        name="energy_purchased_delete",
    ),
    path(
        "energia-wyprodukowana/",
        views.energy_produced_list,
        name="energy_produced_list",
    ),
    path(
        "energia-wyprodukowana/dodaj/",
        views.energy_produced_add,
        name="energy_produced_add",
    ),
    path(
        "energia-wyprodukowana/edytuj/<int:pk>/",
        views.energy_produced_edit,
        name="energy_produced_edit",
    ),
    path(
        "energia-wyprodukowana/usun/<int:pk>/",
        views.energy_produced_delete,
        name="energy_produced_delete",
    ),
    path("energia-sprzedana/", views.energy_sold_list, name="energy_sold_list"),
    path("energia-sprzedana/dodaj/", views.energy_sold_add, name="energy_sold_add"),
    path(
        "energia-sprzedana/edytuj/<int:pk>/",
        views.energy_sold_edit,
        name="energy_sold_edit",
    ),
    path(
        "energia-sprzedana/usun/<int:pk>/",
        views.energy_sold_delete,
        name="energy_sold_delete",
    ),
    path(
        "<int:company_id>/dashboard/", views.DashboardView.as_view(), name="dashboard"
    ),
    path(
        "company/<int:company_id>/stationary/",
        views.StationaryCombustionListView.as_view(),
        name="stationarycombustion-list",
    ),
    path(
        "<int:company_id>/scope1/stationary/add/",
        views.StationaryCombustionCreateView.as_view(),
        name="stationarycombustion-add",
    ),
    path(
        "company/<int:company_id>/stationary/<int:pk>/edit/",
        views.StationaryCombustionUpdateView.as_view(),
        name="stationarycombustion-edit",
    ),
    path(
        "company/<int:company_id>/stationary/<int:pk>/delete/",
        views.StationaryCombustionDeleteView.as_view(),
        name="stationarycombustion-delete",
    ),
    path(
        "<int:company_id>/scope1/mobile/add/",
        views.MobileCombustionCreateView.as_view(),
        name="mobile-add",
    ),
    path(
        "<int:company_id>/scope1/process/add/",
        views.ProcessEmissionCreateView.as_view(),
        name="process-add",
    ),
    path(
        "<int:company_id>/scope1/fugitive/add/",
        views.FugitiveEmissionCreateView.as_view(),
        name="fugitive-add",
    ),
]
