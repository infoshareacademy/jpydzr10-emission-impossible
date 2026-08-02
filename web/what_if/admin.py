from django.contrib import admin

from .models import ReductionGoal, ReductionTarget


@admin.register(ReductionGoal)
class ReductionGoalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_global",
        "company",
        "target_year",
        "reduction_pct",
        "scope",
    )
    list_filter = ("scope", ("company", admin.EmptyFieldListFilter), "target_year")
    search_fields = ("name", "company__name")

    # Opcjonalnie: własna wirtualna kolumna ułatwiająca skanowanie wzrokiem
    @admin.display(boolean=True, description="Cel Globalny")
    def is_global(self, obj):
        return obj.company_id is None


@admin.register(ReductionTarget)
class ReductionTargetAdmin(admin.ModelAdmin):
    list_display = ("company", "goal")
    list_filter = ("company",)