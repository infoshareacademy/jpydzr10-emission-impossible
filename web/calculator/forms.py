from django import forms

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
        ("liquid", "Ciekłe (Liquid)"),
        ("gas", "Gazowe (Gas)"),
        ("solid", "Stałe (Solid)"),
    ]

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label="Kategoria paliwa",
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
    )

    class Meta:
        model = FuelType
        fields = ["name", "symbol", "category"]
        labels = {"name": "Nazwa paliwa", "symbol": "Symbol / Kod"}
        widgets = {
            "name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "np. Olej napędowy"}
            ),
            "symbol": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "np. ON_DIESEL"}
            ),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name"]
        labels = {"name": "Nazwa dostawcy"}
        widgets = {
            "name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "np. PKN ORLEN S.A."}
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
            "fuel_type": "Typ paliwa",
            "supplier": "Dostawca (opcjonalnie)",
            "density_kg_per_m3": "Gęstość (kg/m³)",
            "calorific_mj_per_kg": "Wartość opałowa (MJ/kg)",
            "calorific_mj_per_m3": "Wartość opałowa (MJ/m³)",
            "is_default": "Ustaw jako specyfikację domyślną",
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
