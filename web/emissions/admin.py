from django.contrib import admin

from .models import (
    EmailLog,
    EmissionFactor,
    EnergyConsumption,
    EnergyProduced,
    EnergyPurchased,
    EnergySold,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)


@admin.register(StationaryCombustion)
class StationaryCombustionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "year",
        "company",
        "fuel",
        "amount",
        "unit",
        "emission_tco2eq",
        "created_at",
        "updated_at",
    ]
    list_filter = ["year", "company", "fuel"]
    search_fields = ["company", "fuel"]


@admin.register(MobileCombustion)
class MobileCombustionAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "vehicle", "fuel", "amount", "unit"]
    list_filter = ["year", "company"]
    search_fields = ["company", "vehicle"]


@admin.register(ProcessEmission)
class ProcessEmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "process", "product", "amount"]
    list_filter = ["year", "company"]
    search_fields = ["company", "process"]


@admin.register(FugitiveEmission)
class FugitiveEmissionAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "installation", "product", "amount"]
    list_filter = ["year", "company"]
    search_fields = ["company", "installation"]


@admin.register(EnergyConsumption)
class EnergyConsumptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "year",
        "company",
        "energy_type",
        "amount",
        "unit",
        "emission_tco2eq",
    ]
    list_filter = ["year", "company", "energy_type"]
    search_fields = ["company", "energy_type"]


@admin.register(EnergyPurchased)
class EnergyPurchasedAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "energy_type", "amount", "unit"]
    list_filter = ["year", "company"]
    search_fields = ["company", "energy_type"]


@admin.register(EnergyProduced)
class EnergyProducedAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "energy_type", "amount", "unit"]
    list_filter = ["year", "company"]
    search_fields = ["company", "energy_type"]


@admin.register(EnergySold)
class EnergySoldAdmin(admin.ModelAdmin):
    list_display = ["id", "year", "company", "energy_type", "amount", "unit"]
    list_filter = ["year", "company"]
    search_fields = ["company", "energy_type"]


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ["id", "factor_name", "country", "year", "factor", "unit_factor"]
    list_filter = ["country", "year"]
    search_fields = ["factor_name", "country"]


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ["id", "date", "sender", "company", "template_type", "subject"]
    list_filter = ["company", "template_type"]
    search_fields = ["company", "sender"]
