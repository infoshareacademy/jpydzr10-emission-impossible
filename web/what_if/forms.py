from django import forms

from .models import ReductionTarget


class ReductionTargetForm(forms.ModelForm):
    class Meta:
        model = ReductionTarget
        fields = ["target_name", "base_year", "target_year", "reduction_pct", "scope"]
        widgets = {
            "target_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Np. Redukcja emisji z floty pojazdów",
                }
            ),
            "base_year": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "YYYY"}
            ),
            "target_year": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "YYYY"}
            ),
            "reduction_pct": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Wartość w %",
                }
            ),
            "scope": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        base_year = cleaned_data.get("base_year")
        target_year = cleaned_data.get("target_year")

        if base_year and target_year and base_year >= target_year:
            raise forms.ValidationError(
                "Rok docelowy musi być późniejszy niż rok bazowy."
            )

        return cleaned_data
