from django.contrib import admin

from what_if.models import ReductionTarget


# Register your models here.
@admin.register(ReductionTarget)
class ReductionTargetAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "company",
        "target_name",
        "base_year",
        "target_year",
        "reduction_pct",
    ]
    list_filter = ["company"]
    search_fields = ["company", "target_name"]
