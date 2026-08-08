from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA ADMINA
)

from .models import CustomUser, TOTPDevice, UserCompanyPermission


class UserCompanyPermissionInline(admin.TabularInline):
    model = UserCompanyPermission
    fk_name = "user"
    extra = 1


class TOTPDeviceInline(admin.TabularInline):
    model = TOTPDevice
    fk_name = "user"
    extra = 0
    readonly_fields = ["last_used"]


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [UserCompanyPermissionInline, TOTPDeviceInline]

    # Dodanie pola 'avatar' do sekcji edycji użytkownika
    fieldsets = UserAdmin.fieldsets + (
        (_("Dodatkowe informacje"), {"fields": ("phone_number", "avatar", "role")}),
    )

    # Wyświetlanie miniatury awatara oraz podstawowych kolumn
    list_display = ["avatar_preview", "username", "email", "role", "is_staff"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["username", "email", "phone_number"]

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url,
            )
        return _("Brak")

    avatar_preview.short_description = _("Awatar")


@admin.register(UserCompanyPermission)
class UserCompanyPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "can_read", "can_save"]
    list_filter = ["can_read", "can_save"]
    search_fields = ["user__username", "company__name"]


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "is_active", "confirmed", "last_used"]
    list_filter = ["is_active", "confirmed"]
    search_fields = ["user__username", "name"]
    readonly_fields = ["last_used"]