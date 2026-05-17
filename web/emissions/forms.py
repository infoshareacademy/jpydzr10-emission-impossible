from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import EnergyConsumption

ENERGY_TYPES = [
    ('Energia elektryczna z OZE', 'Energia elektryczna z OZE'),
    ('Energia elektryczna nie OZE', 'Energia elektryczna nie OZE'),
    ('Ciepło z OZE', 'Ciepło z OZE'),
    ('Ciepło nie OZE', 'Ciepło nie OZE'),
    ('Chłód z OZE', 'Chłód z OZE'),
    ('Chłód nie OZE', 'Chłód nie OZE'),
    ('Para Techniczna z OZE', 'Para Techniczna z OZE'),
    ('Para Techniczna nie OZE', 'Para Techniczna nie OZE'),
]

ENERGY_SOURCES = [
    ('Zakupiona', 'Zakupiona'),
    ('Wyprodukowana', 'Wyprodukowana'),
    ('Sprzedana', 'Sprzedana'),
    ('Zużyta', 'Zużyta'),
]

UNITS = [
    ('MWh', 'MWh'),
    ('kWh', 'kWh'),
    ('GJ', 'GJ'),
    ('MJ', 'MJ'),
]

class EnergyConsumptionForm(forms.ModelForm):
    energy_type = forms.ChoiceField(choices=ENERGY_TYPES)
    energy_source = forms.ChoiceField(choices=ENERGY_SOURCES)
    unit = forms.ChoiceField(choices=UNITS)

    class Meta:
        model = EnergyConsumption
        fields = [
            'year', 'company', 'energy_source', 'energy_type',
            'amount', 'unit', 'source'
        ]
        labels = {
            'year': 'Rok',
            'company': 'Firma',
            'energy_source': 'Źródło energii',
            'energy_type': 'Typ energii',
            'amount': 'Ilość',
            'unit': 'Jednostka',
            'source': 'Źródło danych',
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is None:
            return year
        current_year = datetime.now().year
        if year < 2010 or year > current_year:
            raise ValidationError(
                f'Rok musi być między 2010 a {current_year}.'
            )
        return year

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            return amount
        if amount <= 0:
            raise ValidationError('Ilość musi być większa od zera.')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        energy_source = cleaned_data.get('energy_source')
        energy_type = cleaned_data.get('energy_type')
        source = cleaned_data.get('source')
        if not energy_source:
            self.add_error('energy_source', 'Źródło energii jest wymagane.')
        if not energy_type:
            self.add_error('energy_type', 'Typ energii jest wymagany.')
        if not source:
            self.add_error('source', 'Źródło danych jest wymagane.')
        return cleaned_data