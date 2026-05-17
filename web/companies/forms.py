from django import forms
from companies.models import Companies


class CompaniesForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields =['name',
                 'country',
                 'city',
                 'street',
                 'zip',
                 'phone',
                 'mail',
                 'krs',
                 'regon',
                 'nip',
                 'capital_group_name',
                 ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the Company name',
            }),
            'country': forms.Select(attrs={
                'class': 'form-select',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the City name'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the Street name'
            }),
            'zip': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the Zip code'
            }),
            'phone': forms.TelInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the Phone number'
            }),
            'mail': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the Email'
            }),
            'krs': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the KRS number'
            }),
            'regon': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the regon number'
            }),
            'nip': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the NIP code'
            }),
            'capital_group_name': forms.Select(attrs={
                'class': 'form-select',
            })
        }
        
    def clean_krs(self):
        krs = str(self.cleaned_data.get('krs'))

        if len(krs) != 10:
            raise forms.ValidationError("KRS number must consist of exactly 10 digits ")

        return krs

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        cleaned_phone = phone.replace(" ", "").replace("-", "")

        if not cleaned_phone.lstrip('+').isdigit():
            raise forms.ValidationError("A phone number can only contain digits, spaces, hyphens, and the ‘+’ sign.")

        if len(cleaned_phone) < 9:
            raise forms.ValidationError("The phone number is too short.")

        return phone