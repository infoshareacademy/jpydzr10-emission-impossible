from django.contrib import admin

from .models import AIChatMessage, AIChatSession


class AIChatMessageInline(admin.TabularInline):
    model = AIChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False

@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company', 'scope_type', 'is_active')
    list_filter = ('scope_type', 'is_active', 'company')
    search_fields = ('user__username', 'company__name')
    inlines = [AIChatMessageInline]

@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)