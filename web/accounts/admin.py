# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, UserCompanyPermission


class UserCompanyPermissionInline(admin.TabularInline):
    model = UserCompanyPermission
    fk_name = "user"
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [UserCompanyPermissionInline]
    fieldsets = UserAdmin.fieldsets + (
        ("Dodatkowe", {"fields": ("phone_number", "role")}),
    )
    list_display = ["username", "email", "role", "is_staff"]


@admin.register(UserCompanyPermission)
class UserCompanyPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "can_read", "can_save"]
