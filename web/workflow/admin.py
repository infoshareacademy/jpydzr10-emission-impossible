from django.contrib import admin

from .models import CompanyReportEnvelope, RecordComment, ReportingPeriod, Task


@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ("year", "is_active", "deadline")


@admin.register(CompanyReportEnvelope)
class CompanyReportEnvelopeAdmin(admin.ModelAdmin):
    list_display = ("company", "period", "status")
    list_filter = ("status", "period")


admin.site.register(RecordComment)
admin.site.register(Task)
