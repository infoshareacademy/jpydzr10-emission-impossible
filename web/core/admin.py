from django.contrib import admin

from core.models import ChangeLog

@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ['id_rejestr_zmian', 'login', 'date_change', 'table_name', 'change_type']
    list_filter = ['change_type', 'table_name']
    search_fields = ['login', 'table_name']