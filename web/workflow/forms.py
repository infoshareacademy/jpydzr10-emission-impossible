from django import forms

from .models import ReportingPeriod


class ReportingPeriodForm(forms.ModelForm):
    class Meta:
        model = ReportingPeriod
        fields = ["year", "deadline", "is_active"]
        widgets = {
            "year": forms.NumberInput(
                attrs={
                    "class": "w-full bg-white/5 border border-[#1a4a52] rounded-xl text-[#e8f4f0] font-mono text-sm p-3 focus:outline-none focus:border-[#c8f535] transition-colors",
                    "placeholder": "np. 2026",
                }
            ),
            "deadline": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full bg-white/5 border border-[#1a4a52] rounded-xl text-[#e8f4f0] font-mono text-sm p-3 focus:outline-none focus:border-[#c8f535] transition-colors",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "w-5 h-5 rounded border-[#1a4a52] text-[#1a4a52] focus:ring-[#c8f535] bg-white/5"
                }
            ),
        }
