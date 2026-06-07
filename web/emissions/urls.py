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
    # DASHBOARD
    path(
        "<int:company_id>/dashboard/", views.DashboardView.as_view(), name="dashboard"
    ),
    # SPALANIE STACJONARNE (Stationary Combustion)
    path(
        "company/<int:company_id>/stationary/",
        views.StationaryCombustionListView.as_view(),
        name="stationarycombustion-list",
    ),
    path(
        "company/<int:company_id>/stationary/add/",
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
    # SPALANIE MOBILNE (Mobile Combustion)
    path(
        "company/<int:company_id>/mobile/",
        views.MobileCombustionListView.as_view(),
        name="mobilecombustion-list",
    ),
    path(
        "company/<int:company_id>/mobile/add/",
        views.MobileCombustionCreateView.as_view(),
        name="mobilecombustion-add",
    ),
    path(
        "company/<int:company_id>/mobile/<int:pk>/edit/",
        views.MobileCombustionUpdateView.as_view(),
        name="mobilecombustion-edit",
    ),
    path(
        "company/<int:company_id>/mobile/<int:pk>/delete/",
        views.MobileCombustionDeleteView.as_view(),
        name="mobilecombustion-delete",
    ),
    # EMISJA PROCESOWA (Process Emission)
    path(
        "company/<int:company_id>/process/",
        views.ProcessEmissionListView.as_view(),
        name="processemission-list",
    ),
    path(
        "company/<int:company_id>/process/add/",
        views.ProcessEmissionCreateView.as_view(),
        name="processemission-add",
    ),
    path(
        "company/<int:company_id>/process/<int:pk>/edit/",
        views.ProcessEmissionUpdateView.as_view(),
        name="processemission-edit",
    ),
    path(
        "company/<int:company_id>/process/<int:pk>/delete/",
        views.ProcessEmissionDeleteView.as_view(),
        name="processemission-delete",
    ),
    # EMISJA NIEZORGANIZOWANA (Fugitive Emission)
    path(
        "company/<int:company_id>/fugitive/",
        views.FugitiveEmissionListView.as_view(),
        name="fugitiveemission-list",
    ),
    path(
        "company/<int:company_id>/fugitive/add/",
        views.FugitiveEmissionCreateView.as_view(),
        name="fugitiveemission-add",
    ),
    path(
        "company/<int:company_id>/fugitive/<int:pk>/edit/",
        views.FugitiveEmissionUpdateView.as_view(),
        name="fugitiveemission-edit",
    ),
    path(
        "company/<int:company_id>/fugitive/<int:pk>/delete/",
        views.FugitiveEmissionDeleteView.as_view(),
        name="fugitiveemission-delete",
    ),
    # --- SŁOWNIK WSKAŹNIKÓW EMISJI ---
    path("factors/", views.EmissionFactorListView.as_view(), name="factor-list"),
    path("factors/add/", views.EmissionFactorCreateView.as_view(), name="factor-add"),
    path(
        "factors/<int:pk>/edit/",
        views.EmissionFactorUpdateView.as_view(),
        name="factor-edit",
    ),
    path(
        "factors/<int:pk>/delete/",
        views.EmissionFactorDeleteView.as_view(),
        name="factor-delete",
    ),
]
