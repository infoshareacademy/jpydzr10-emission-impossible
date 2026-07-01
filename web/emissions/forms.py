from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from .models import (
    EnergyConsumption,
    EmissionFactor,
    EnergyProduced,
    EnergyPurchased,
    EnergySold,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)

ENERGY_TYPES = [
    ("Energia elektryczna z OZE", "Energia elektryczna z OZE"),
    ("Energia elektryczna nie OZE", "Energia elektryczna nie OZE"),
    ("Ciepło z OZE", "Ciepło z OZE"),
    ("Ciepło nie OZE", "Ciepło nie OZE"),
    ("Chłód z OZE", "Chłód z OZE"),
    ("Chłód nie OZE", "Chłód nie OZE"),
    ("Para Techniczna z OZE", "Para Techniczna z OZE"),
    ("Para Techniczna nie OZE", "Para Techniczna nie OZE"),
]

ENERGY_SOURCES = [
    ("Zakupiona", "Zakupiona"),
    ("Wyprodukowana", "Wyprodukowana"),
    ("Sprzedana", "Sprzedana"),
    ("Zużyta", "Zużyta"),
]

UNITS = [
    ("MWh", "MWh"),
    ("kWh", "kWh"),
    ("GJ", "GJ"),
    ("MJ", "MJ"),
]


class EnergyConsumptionForm(forms.ModelForm):
    energy_type = forms.ChoiceField(choices=ENERGY_TYPES)
    energy_source = forms.ChoiceField(choices=ENERGY_SOURCES)
    unit = forms.ChoiceField(choices=UNITS)

    class Meta:
        model = EnergyConsumption
        fields = [
            "year",
            "company",
            "energy_source",
            "energy_type",
            "amount",
            "unit",
            "source",
        ]
        labels = {
            "year": _("Rok"),
            "company": _("Firma"),
            "energy_source": _("Źródło energii"),
            "energy_type": _("Typ energii"),
            "amount": _("Ilość"),
            "unit": _("Jednostka"),
            "source": _("Źródło danych"),
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is None:
            return year
        current_year = timezone.now().year
        if year < 2010 or year > current_year:
            raise ValidationError(
                _("Rok musi być między 2010 a %(current_year)s."),
                params={"current_year": current_year},
            )
        return year

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return amount
        if amount <= 0:
            raise ValidationError(_("Ilość musi być większa od zera."))
        return amount

    def clean(self):
        cleaned_data = super().clean()
        energy_source = cleaned_data.get("energy_source")
        energy_type = cleaned_data.get("energy_type")
        source = cleaned_data.get("source")
        if not energy_source:
            self.add_error("energy_source", "Źródło energii jest wymagane.")
        if not energy_type:
            self.add_error("energy_type", "Typ energii jest wymagany.")
        if not source:
            self.add_error("source", "Źródło danych jest wymagane.")
        return cleaned_data


class EnergyPurchasedForm(forms.ModelForm):
    energy_type = forms.ChoiceField(choices=ENERGY_TYPES)
    unit = forms.ChoiceField(choices=UNITS)

    class Meta:
        model = EnergyPurchased
        fields = [
            "year",
            "company",
            "energy_type",
            "amount",
            "unit",
            "trader",
            "source",
        ]
        labels = {
            "year": _("Rok"),
            "company": _("Firma"),
            "energy_type": _("Typ energii"),
            "amount": _("Ilość"),
            "unit": _("Jednostka"),
            "trader": _("Dostawca"),
            "source": _("Źródło danych"),
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is None:
            return year
        current_year = timezone.now().year
        if year < 2010 or year > current_year:
            raise ValidationError(
                _("Rok musi być między 2010 a %(current_year)s."),
                params={"current_year": current_year},
            )
        return year

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return amount
        if amount <= 0:
            raise ValidationError(_("Ilość musi być większa od zera."))
        return amount


class EnergyProducedForm(forms.ModelForm):
    energy_type = forms.ChoiceField(choices=ENERGY_TYPES)
    unit = forms.ChoiceField(choices=UNITS)

    class Meta:
        model = EnergyProduced
        fields = [
            "year",
            "company",
            "energy_type",
            "amount",
            "unit",
            "installation",
            "source",
        ]
        labels = {
            "year": _("Rok"),
            "company": _("Firma"),
            "energy_type": _("Typ energii"),
            "amount": _("Ilość"),
            "unit": _("Jednostka"),
            "installation": _("Instalacja"),
            "source": _("Źródło danych"),
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is None:
            return year
        current_year = timezone.now().year
        if year < 2010 or year > current_year:
            raise ValidationError(
                _("Rok musi być między 2010 a %(current_year)s."),
                params={"current_year": current_year},
            )
        return year

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return amount
        if amount <= 0:
            raise ValidationError(_("Ilość musi być większa od zera."))
        return amount


class EnergySoldForm(forms.ModelForm):
    energy_type = forms.ChoiceField(choices=ENERGY_TYPES)
    unit = forms.ChoiceField(choices=UNITS)

    class Meta:
        model = EnergySold
        fields = [
            "year",
            "company",
            "energy_type",
            "amount",
            "unit",
            "customer",
            "source",
        ]
        labels = {
            "year": _("Rok"),
            "company": _("Firma"),
            "energy_type": _("Typ energii"),
            "amount": _("Ilość"),
            "unit": _("Jednostka"),
            "customer": _("Odbiorca"),
            "source": _("Źródło danych"),
        }
        widgets = {
            "year": forms.NumberInput(attrs={"min": 2010}),
            "amount": forms.NumberInput(attrs={"min": 0.01}),
        }

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is None:
            return year
        current_year = timezone.now().year
        if year < 2010 or year > current_year:
            raise ValidationError(
                _("Rok musi być między 2010 a %(current_year)s."),
                params={"current_year": current_year},
            )
        return year


class Scope1BaseForm(forms.ModelForm):
    """
    Klasa bazowa dla wszystkich formularzy Zakresu 1.
    Automatycznie nakłada brutalistyczne style Tailwind na każde pole.
    """

    HIDDEN_FIELDS = {
        "created_by",
        "updated_by",
        "note",
        "company",
    }
    READONLY_FIELDS = {
        "calculated_emission_tco2eq",
        "applied_factor_value",
        "applied_factor_unit",
        "applied_converter_value",
        "applied_converter_unit",
        "company",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Usuń ukryte pola całkowicie z formularza
        for field_name in self.HIDDEN_FIELDS:
            if field_name in self.fields:
                del self.fields[field_name]

        for field_name, field in self.fields.items():
            # Pola tylko do odczytu
            if field_name in self.READONLY_FIELDS:
                field.required = False
                field.widget.attrs.update(
                    {
                        "readonly": True,
                        "disabled": True,
                        "class": (
                            "w-full px-4 py-2 bg-gray-100 border-2 border-gray-300 "
                            "text-gray-500 cursor-not-allowed outline-none font-body-md"
                        ),
                    }
                )
            else:
                # Standardowe pola — istniejący styl brutalistyczny
                field.widget.attrs.update(
                    {
                        "class": (
                            "w-full px-4 py-2 bg-white border-2 border-black "
                            "shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] "
                            "focus:translate-x-[1px] focus:translate-y-[1px] "
                            "focus:shadow-none transition-all outline-none font-body-md"
                        )
                    }
                )
                if not field.widget.attrs.get("placeholder"):
                    label = field.label or field_name
                    field.widget.attrs["placeholder"] = f"Wprowadź: {label}"


class StationaryCombustionForm(Scope1BaseForm):
    class Meta:
        model = StationaryCombustion
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class MobileCombustionForm(Scope1BaseForm):
    class Meta:
        model = MobileCombustion
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ProcessEmissionForm(Scope1BaseForm):
    class Meta:
        model = ProcessEmission
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class FugitiveEmissionForm(Scope1BaseForm):
    class Meta:
        model = FugitiveEmission
        fields = "__all__"
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class EmissionFactorForm(forms.ModelForm):
    class Meta:
        model = EmissionFactor
        fields = ["year", "factor_name", "factor", "unit_factor", "source", "country"]


# ===== IMPORT DANYCH =====
class EnergyConsumptionImportForm(forms.Form):
    """Formularz do wgrywania pliku XLSX z danymi."""

    file = forms.FileField(
        label=_('Wybierz plik XLSX'),
        help_text=_('Maksymalny rozmiar: 5MB'),
        widget=forms.FileInput(attrs={
            'accept': '.xlsx',
            'class': 'form-control'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.xlsx'):
                raise ValidationError(_('Obsługiwany jest tylko format .xlsx'))
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(_('Plik jest za duży (max 5MB)'))
        return file


class EnergyPurchasedImportForm(forms.Form):
    """Formularz do wgrywania pliku XLSX z danymi zakupionej energii."""

    file = forms.FileField(
        label=_('Wybierz plik XLSX'),
        help_text=_('Maksymalny rozmiar: 5MB'),
        widget=forms.FileInput(attrs={
            'accept': '.xlsx',
            'class': 'form-control'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.xlsx'):
                raise ValidationError(_('Obsługiwany jest tylko format .xlsx'))
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(_('Plik jest za duży (max 5MB)'))
        return file


class EnergyProducedImportForm(forms.Form):
    """Formularz do wgrywania pliku XLSX z danymi wyprodukowanej energii."""

    file = forms.FileField(
        label=_('Wybierz plik XLSX'),
        help_text=_('Maksymalny rozmiar: 5MB'),
        widget=forms.FileInput(attrs={
            'accept': '.xlsx',
            'class': 'form-control'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.xlsx'):
                raise ValidationError(_('Obsługiwany jest tylko format .xlsx'))
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(_('Plik jest za duży (max 5MB)'))
        return file


class EnergySoldImportForm(forms.Form):
    """Formularz do wgrywania pliku XLSX z danymi sprzedanej energii."""

    file = forms.FileField(
        label=_('Wybierz plik XLSX'),
        help_text=_('Maksymalny rozmiar: 5MB'),
        widget=forms.FileInput(attrs={
            'accept': '.xlsx',
            'class': 'form-control'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.xlsx'):
                raise ValidationError(_('Obsługiwany jest tylko format .xlsx'))
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(_('Plik jest za duży (max 5MB)'))
        return file