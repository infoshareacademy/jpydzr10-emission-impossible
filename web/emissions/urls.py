from django.urls import path
from . import views

app_name = 'emissions'

urlpatterns = [
    # Energy Consumption
    path('energia/', views.EnergyConsumptionListView.as_view(), name='energy_consumption_list'),
    path('energia/dodaj/', views.EnergyConsumptionCreateView.as_view(), name='energy_consumption_add'),
    path('energia/edytuj/<int:pk>/', views.EnergyConsumptionUpdateView.as_view(), name='energy_consumption_edit'),
    path('energia/usun/<int:pk>/', views.EnergyConsumptionDeleteView.as_view(), name='energy_consumption_delete'),

    # Energy Purchased
    path('energia-zakupiona/', views.EnergyPurchasedListView.as_view(), name='energy_purchased_list'),
    path('energia-zakupiona/dodaj/', views.EnergyPurchasedCreateView.as_view(), name='energy_purchased_add'),
    path('energia-zakupiona/edytuj/<int:pk>/', views.EnergyPurchasedUpdateView.as_view(), name='energy_purchased_edit'),
    path('energia-zakupiona/usun/<int:pk>/', views.EnergyPurchasedDeleteView.as_view(), name='energy_purchased_delete'),

    # Energy Produced
    path('energia-wyprodukowana/', views.EnergyProducedListView.as_view(), name='energy_produced_list'),
    path('energia-wyprodukowana/dodaj/', views.EnergyProducedCreateView.as_view(), name='energy_produced_add'),
    path('energia-wyprodukowana/edytuj/<int:pk>/', views.EnergyProducedUpdateView.as_view(),
         name='energy_produced_edit'),
    path('energia-wyprodukowana/usun/<int:pk>/', views.EnergyProducedDeleteView.as_view(),
         name='energy_produced_delete'),

    # Energy Sold
    path('energia-sprzedana/', views.EnergySoldListView.as_view(), name='energy_sold_list'),
    path('energia-sprzedana/dodaj/', views.EnergySoldCreateView.as_view(), name='energy_sold_add'),
    path('energia-sprzedana/edytuj/<int:pk>/', views.EnergySoldUpdateView.as_view(), name='energy_sold_edit'),
    path('energia-sprzedana/usun/<int:pk>/', views.EnergySoldDeleteView.as_view(), name='energy_sold_delete'),

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

    # Energy Consumption Import
    path('energia/szablon/', views.EnergyConsumptionTemplateDownloadView.as_view(), name='energy_consumption_template'),
    path('energia/importuj/', views.EnergyConsumptionImportView.as_view(), name='energy_consumption_import'),

    # Energy Purchased Import
    path('energia-zakupiona/szablon/', views.EnergyPurchasedTemplateDownloadView.as_view(), name='energy_purchased_template'),
    path('energia-zakupiona/importuj/', views.EnergyPurchasedImportView.as_view(), name='energy_purchased_import'),

    # Energy Produced Import
    path('energia-wyprodukowana/szablon/', views.EnergyProducedTemplateDownloadView.as_view(), name='energy_produced_template'),
    path('energia-wyprodukowana/importuj/', views.EnergyProducedImportView.as_view(), name='energy_produced_import'),

    # Energy Sold Import
    path('energia-sprzedana/szablon/', views.EnergySoldTemplateDownloadView.as_view(), name='energy_sold_template'),
    path('energia-sprzedana/importuj/', views.EnergySoldImportView.as_view(), name='energy_sold_import'),
]
