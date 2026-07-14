from companies.models import Companies
from django import forms
from django.db.models import Q
from emissions.models import EmissionFactor

from .models import ReductionGoal, ReductionTarget


class ReductionTargetForm(forms.ModelForm):
    class Meta:
        model = ReductionTarget
        fields = ["goal"]
        labels = {
            "goal": "Wybierz cel korporacyjny"
        }
        widgets = {
            "goal": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        self.fields["goal"].empty_label = "-- Wybierz cel z listy --"

        if company:
            qs = ReductionGoal.objects.filter(
                Q(company__isnull=True) | Q(company=company)
            ).order_by("company", "-target_year", "name")
            self.fields["goal"].queryset = qs
        else:
            self.fields["goal"].queryset = ReductionGoal.objects.none()


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
