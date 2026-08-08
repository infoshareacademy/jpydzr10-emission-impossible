from django.contrib import admin
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA ADMINA
)

from companies.models import Companies, CompaniesGroup, Countries


@admin.register(CompaniesGroup)
class AdminCompaniesGroup(admin.ModelAdmin):
    list_display = ["gk_name", "lvl_in_structure"]
    search_fields = ["gk_name"]
    list_filter = ["gk_name"]


@admin.register(Companies)
class AdminCompanies(admin.ModelAdmin):
    list_display = [
        "name",
        "country",
        "city",
        "street",
        "zip",
        "phone",
        "mail",
        "krs",
        "regon",
        "nip",
        "capital_group_name",
    ]
    search_fields = ["name"]
    list_filter = ["name", "country", "regon", "nip"]


@admin.register(Countries)
class AdminCountries(admin.ModelAdmin):
    list_display = ["name", "code_alfa_2"]
    search_fields = ["name", "code_alfa_2"]
    list_filter = ["name"]