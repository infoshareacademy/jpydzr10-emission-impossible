from companies.models import Companies
from django import forms
from emissions.models import EmissionFactor

from what_if.models import ReductionTarget


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


class SimulationForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=Companies.objects.none(),
        required=False,
        empty_label="-- Cała organizacja (Wszystkie spółki) --",
        label="Spółka do symulacji",
    )

    current_factor = forms.ModelChoiceField(
        queryset=EmissionFactor.objects.all(),
        required=True,
        label="Co zastępujemy? (Obecne źródło)",
        help_text="Wybierz paliwo/energię, z której rezygnujesz.",
    )
    reduced_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=3,
        required=True,
        min_value=0,
        label="Ilość redukowana",
        help_text="Ilość zużycia, którą usuwasz z bilansu.",
    )

    new_factor = forms.ModelChoiceField(
        queryset=EmissionFactor.objects.all(),
        required=True,
        label="Czym zastępujemy? (Nowe źródło)",
        help_text="Wybierz nowe paliwo/energię zastępczą.",
    )
    added_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=3,
        required=True,
        min_value=0,
        label="Ilość dodawana",
        help_text="Ilość nowego zużycia (pamiętaj o odpowiedniej jednostce wskaźnika!).",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            if user.role == "admin" or user.is_superuser:
                self.fields["company"].queryset = Companies.objects.all().order_by(
                    "name"
                )
            else:
                self.fields["company"].queryset = (
                    Companies.objects.filter(
                        user_permissions__user=user, user_permissions__can_read=True
                    )
                    .distinct()
                    .order_by("name")
                )
                self.fields["company"].required = True
                self.fields["company"].empty_label = None

        factor_label = lambda obj: f"{obj.factor_name} ({obj.factor} {obj.unit_factor})"
        self.fields["current_factor"].label_from_instance = factor_label
        self.fields["new_factor"].label_from_instance = factor_label
