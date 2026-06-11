from django.contrib import admin

from .models import FuelSpec, FuelType, Supplier


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    # Kolumny widoczne na liście obiektów
    list_display = ("name", "symbol", "category")
    # Filtry w prawym pasku bocznym
    list_filter = ("category",)
    # Pola, po których można wyszukiwać
    search_fields = ("name", "symbol")
    # Domyślne sortowanie
    ordering = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(FuelSpec)
class FuelSpecAdmin(admin.ModelAdmin):
    list_display = (
        "fuel_type",
        "supplier",
        "is_default",
        "density_kg_per_m3",
        "calorific_mj_per_kg",
        "calorific_mj_per_m3",
    )
    list_filter = ("is_default", "fuel_type__category", "supplier")
    search_fields = ("fuel_type__name", "supplier__name")
    autocomplete_fields = ("fuel_type", "supplier")

    fieldsets = (
        (
            "Informacje podstawowe",
            {
                "fields": ("fuel_type", "supplier", "is_default"),
                "description": "Wybierz typ paliwa i dostawcę. Pozostaw dostawcę puste dla specyfikacji domyślnej.",
            },
        ),
        (
            "Parametry fizykochemiczne",
            {
                "fields": (
                    "density_kg_per_m3",
                    "calorific_mj_per_kg",
                    "calorific_mj_per_m3",
                ),
            },
        ),
    )
