from django.contrib import admin

from .models import UserCarbonFootprint


@admin.register(UserCarbonFootprint)
class UserCarbonFootprintAdmin(admin.ModelAdmin):
  list_display = (
      'user',
      'get_formatted_emissions',
      'total_requests',
      'last_updated',
  )
  search_fields = ('user__username', 'user__email')
  readonly_fields = (
      'last_updated',
  )  # Opcjonalnie: żeby data ostatniej aktualizacji była tylko do odczytu
  list_filter = ('last_updated',)
  ordering = ('-total_emissions_kg',)  # Domyślnie sortuj od największego śladu

  @admin.display(
      description='Całkowita emisja (kg CO₂eq)',
      ordering='total_emissions_kg',
  )
  def get_formatted_emissions(self, obj):
    return f'{obj.total_emissions_kg:.6f} kg CO₂eq'