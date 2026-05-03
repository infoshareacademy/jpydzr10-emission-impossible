from django.contrib import admin
from .models import (
    StationaryCombustion, MobileCombustion, ProcessEmission,
    FugitiveEmission, EnergyConsumption, EnergyPurchased,
    EnergyProduced, EnergySold, EmissionFactor, UnitConverter,
    ReductionTarget, EmailLog, ChangeLog
)

@admin.register(StationaryCombustion)
class StationaryCombustionAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'fuel', 'amount', 'unit', 'emission_tco2eq']
    list_filter = ['year', 'company', 'fuel']
    search_fields = ['company', 'fuel']

@admin.register(MobileCombustion)
class MobileCombustionAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'vehicle', 'fuel', 'amount', 'unit']
    list_filter = ['year', 'company']
    search_fields = ['company', 'vehicle']

@admin.register(ProcessEmission)
class ProcessEmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'process', 'product', 'amount']
    list_filter = ['year', 'company']
    search_fields = ['company', 'process']

@admin.register(FugitiveEmission)
class FugitiveEmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'installation', 'product', 'amount']
    list_filter = ['year', 'company']
    search_fields = ['company', 'installation']

@admin.register(EnergyConsumption)
class EnergyConsumptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'energy_type', 'amount', 'unit', 'emission_tco2eq']
    list_filter = ['year', 'company', 'energy_type']
    search_fields = ['company', 'energy_type']

@admin.register(EnergyPurchased)
class EnergyPurchasedAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'energy_type', 'amount', 'unit']
    list_filter = ['year', 'company']
    search_fields = ['company', 'energy_type']

@admin.register(EnergyProduced)
class EnergyProducedAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'energy_type', 'amount', 'unit']
    list_filter = ['year', 'company']
    search_fields = ['company', 'energy_type']

@admin.register(EnergySold)
class EnergySoldAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'company', 'energy_type', 'amount', 'unit']
    list_filter = ['year', 'company']
    search_fields = ['company', 'energy_type']

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['id', 'factor_name', 'country', 'year', 'factor', 'unit_factor']
    list_filter = ['country', 'year']
    search_fields = ['factor_name', 'country']

@admin.register(UnitConverter)
class UnitConverterAdmin(admin.ModelAdmin):
    list_display = ['id', 'unit_from', 'unit_to', 'factor']
    search_fields = ['unit_from', 'unit_to']

@admin.register(ReductionTarget)
class ReductionTargetAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'target_name', 'base_year', 'target_year', 'reduction_pct']
    list_filter = ['company']
    search_fields = ['company', 'target_name']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'sender', 'company', 'template_type', 'subject']
    list_filter = ['company', 'template_type']
    search_fields = ['company', 'sender']

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ['id_rejestr_zmian', 'login', 'date_change', 'table_name', 'change_type']
    list_filter = ['change_type', 'table_name']
    search_fields = ['login', 'table_name']

# Register your models here.
