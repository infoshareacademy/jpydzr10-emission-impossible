from django import forms
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA FORMULARZY
)

from .models import FuelSpec, FuelType, Supplier

# Wspólny zestaw klas dla pól tekstowych/numerycznych/selectów
INPUT_CLASSES = (
    "w-full bg-[rgba(17,23,32,0.6)] border border-border-subtle focus:border-accent "
    "text-text-main px-4 py-2.5 font-mono text-sm rounded-sm outline-none transition-colors"
)

CHECKBOX_CLASSES = (
    "rounded-sm border-border-subtle text-accent focus:ring-accent "
    "bg-[rgba(17,23,32,0.6)] w-4 h-4 transition-colors"
)


class FuelTypeForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ("liquid", _("Ciekłe (Liquid)")),
        ("gas", _("Gazowe (Gas)")),
        ("solid", _("Stałe (Solid)")),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label=_("Kategoria paliwa"),
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
    )

    class Meta:
        model = FuelType
        fields = ["name", "symbol", "category"]
        labels = {"name": _("Nazwa paliwa"), "symbol": _("Symbol / Kod")}
        widgets = {
            "name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": _("np. Olej napędowy")}
            ),
            "symbol": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": _("np. ON_DIESEL")}
            ),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name"]
        labels = {"name": _("Nazwa dostawcy")}
        widgets = {
            "name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": _("np. PKN ORLEN S.A.")}
            ),
        }


class FuelSpecForm(forms.ModelForm):
    class Meta:
        model = FuelSpec
        fields = [
            "fuel_type",
            "supplier",
            "density_kg_per_m3",
            "calorific_mj_per_kg",
            "calorific_mj_per_m3",
            "is_default",
        ]
        labels = {
            "fuel_type": _("Typ paliwa"),
            "supplier": _("Dostawca (opcjonalnie)"),
            "density_kg_per_m3": _("Gęstość (kg/m³)"),
            "calorific_mj_per_kg": _("Wartość opałowa (MJ/kg)"),
            "calorific_mj_per_m3": _("Wartość opałowa (MJ/m³)"),
            "is_default": _("Ustaw jako specyfikację domyślną"),
        }
        widgets = {
            "fuel_type": forms.Select(attrs={"class": INPUT_CLASSES}),
            "supplier": forms.Select(attrs={"class": INPUT_CLASSES}),
            "density_kg_per_m3": forms.NumberInput(
                attrs={"class": INPUT_CLASSES, "step": "any", "placeholder": "0.00"}
            ),
            "calorific_mj_per_kg": forms.NumberInput(
                attrs={"class": INPUT_CLASSES, "step": "any", "placeholder": "0.00"}
            ),
            "calorific_mj_per_m3": forms.NumberInput(
                attrs={"class": INPUT_CLASSES, "step": "any", "placeholder": "0.00"}
            ),
            "is_default": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASSES}),
        }