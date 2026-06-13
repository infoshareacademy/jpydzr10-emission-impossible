from django.urls import path

from . import views
from . import views_import as import_views

app_name = "emissions"

urlpatterns = [
    # =========================================================================
    # SCOPE 2 — Zużycie energii (Energy Consumption)
    # =========================================================================
    path(
        "energia/",
        views.EnergyConsumptionListView.as_view(),
        name="energy_consumption_list",
    ),
    path(
        "energia/dodaj/",
        views.EnergyConsumptionCreateView.as_view(),
        name="energy_consumption_add",
    ),
    path(
        "energia/edytuj/<int:pk>/",
        views.EnergyConsumptionUpdateView.as_view(),
        name="energy_consumption_edit",
    ),
    path(
        "energia/usun/<int:pk>/",
        views.EnergyConsumptionDeleteView.as_view(),
        name="energy_consumption_delete",
    ),
    # =========================================================================
    # SCOPE 2 — Zakupiona energia (Energy Purchased)
    # =========================================================================
    path(
        "energia-zakupiona/",
        views.EnergyPurchasedListView.as_view(),
        name="energy_purchased_list",
    ),
    path(
        "energia-zakupiona/dodaj/",
        views.EnergyPurchasedCreateView.as_view(),
        name="energy_purchased_add",
    ),
    path(
        "energia-zakupiona/edytuj/<int:pk>/",
        views.EnergyPurchasedUpdateView.as_view(),
        name="energy_purchased_edit",
    ),
    path(
        "energia-zakupiona/usun/<int:pk>/",
        views.EnergyPurchasedDeleteView.as_view(),
        name="energy_purchased_delete",
    ),
    # =========================================================================
    # SCOPE 2 — Wyprodukowana energia (Energy Produced)
    # =========================================================================
    path(
        "energia-wyprodukowana/",
        views.EnergyProducedListView.as_view(),
        name="energy_produced_list",
    ),
    path(
        "energia-wyprodukowana/dodaj/",
        views.EnergyProducedCreateView.as_view(),
        name="energy_produced_add",
    ),
    path(
        "energia-wyprodukowana/edytuj/<int:pk>/",
        views.EnergyProducedUpdateView.as_view(),
        name="energy_produced_edit",
    ),
    path(
        "energia-wyprodukowana/usun/<int:pk>/",
        views.EnergyProducedDeleteView.as_view(),
        name="energy_produced_delete",
    ),
    # =========================================================================
    # SCOPE 2 — Sprzedana energia (Energy Sold)
    # =========================================================================
    path(
        "energia-sprzedana/",
        views.EnergySoldListView.as_view(),
        name="energy_sold_list",
    ),
    path(
        "energia-sprzedana/dodaj/",
        views.EnergySoldCreateView.as_view(),
        name="energy_sold_add",
    ),
    path(
        "energia-sprzedana/edytuj/<int:pk>/",
        views.EnergySoldUpdateView.as_view(),
        name="energy_sold_edit",
    ),
    path(
        "energia-sprzedana/usun/<int:pk>/",
        views.EnergySoldDeleteView.as_view(),
        name="energy_sold_delete",
    ),
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    path(
        "<int:company_id>/dashboard/",
        views.DashboardView.as_view(),
        name="dashboard",
    ),
    # =========================================================================
    # SCOPE 1 — Spalanie stacjonarne (Stationary Combustion)
    # =========================================================================
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
    # Szablon + Import — Spalanie stacjonarne
    path(
        "company/<int:company_id>/stationary/szablon/",
        import_views.StationaryCombustionTemplateDownloadView.as_view(),
        name="stationarycombustion-template",
    ),
    path(
        "company/<int:company_id>/stationary/importuj/",
        import_views.StationaryCombustionImportView.as_view(),
        name="stationarycombustion-import",
    ),
    # =========================================================================
    # SCOPE 1 — Spalanie mobilne (Mobile Combustion)
    # =========================================================================
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
    # Szablon + Import — Spalanie mobilne
    path(
        "company/<int:company_id>/mobile/szablon/",
        import_views.MobileCombustionTemplateDownloadView.as_view(),
        name="mobilecombustion-template",
    ),
    path(
        "company/<int:company_id>/mobile/importuj/",
        import_views.MobileCombustionImportView.as_view(),
        name="mobilecombustion-import",
    ),
    # =========================================================================
    # SCOPE 1 — Emisje procesowe (Process Emission)
    # =========================================================================
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
    # Szablon + Import — Emisje procesowe
    path(
        "company/<int:company_id>/process/szablon/",
        import_views.ProcessEmissionTemplateDownloadView.as_view(),
        name="processemission-template",
    ),
    path(
        "company/<int:company_id>/process/importuj/",
        import_views.ProcessEmissionImportView.as_view(),
        name="processemission-import",
    ),
    # =========================================================================
    # SCOPE 1 — Emisje niezorganizowane (Fugitive Emission)
    # =========================================================================
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
    # Szablon + Import — Emisje niezorganizowane
    path(
        "company/<int:company_id>/fugitive/szablon/",
        import_views.FugitiveEmissionTemplateDownloadView.as_view(),
        name="fugitiveemission-template",
    ),
    path(
        "company/<int:company_id>/fugitive/importuj/",
        import_views.FugitiveEmissionImportView.as_view(),
        name="fugitiveemission-import",
    ),
    # =========================================================================
    # SŁOWNIK — Wskaźniki emisji (Emission Factors)
    # =========================================================================
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
    # =========================================================================
    # SCOPE 2 — Import i szablony (istniejące)
    # =========================================================================
    path(
        "energia/szablon/",
        views.EnergyConsumptionTemplateDownloadView.as_view(),
        name="energy_consumption_template",
    ),
    path(
        "energia/importuj/",
        views.EnergyConsumptionImportView.as_view(),
        name="energy_consumption_import",
    ),
    path(
        "energia-zakupiona/szablon/",
        views.EnergyPurchasedTemplateDownloadView.as_view(),
        name="energy_purchased_template",
    ),
    path(
        "energia-zakupiona/importuj/",
        views.EnergyPurchasedImportView.as_view(),
        name="energy_purchased_import",
    ),
    path(
        "energia-wyprodukowana/szablon/",
        views.EnergyProducedTemplateDownloadView.as_view(),
        name="energy_produced_template",
    ),
    path(
        "energia-wyprodukowana/importuj/",
        views.EnergyProducedImportView.as_view(),
        name="energy_produced_import",
    ),
    path(
        "energia-sprzedana/szablon/",
        views.EnergySoldTemplateDownloadView.as_view(),
        name="energy_sold_template",
    ),
    path(
        "energia-sprzedana/importuj/",
        views.EnergySoldImportView.as_view(),
        name="energy_sold_import",
    ),
]
