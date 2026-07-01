from django import forms

from companies.models import Companies


class CompaniesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "w-full px-4 py-2 bg-white border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] focus:translate-x-[1px] focus:translate-y-[1px] focus:shadow-none transition-all outline-none font-body-md"
                }
            )
            if not field.widget.attrs.get("placeholder"):
                field.widget.attrs["placeholder"] = (
                    f"Wprowadź {field.label.lower() if field.label else field_name}"
                )

    class Meta:
        model = Companies
        exclude = ["created_at", "updated_at", "created_by", "updated_by"]

    def clean_krs(self):
        krs = str(self.cleaned_data.get("krs"))

        if len(krs) != 10:
            raise forms.ValidationError("KRS number must consist of exactly 10 digits ")

        return krs

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        cleaned_phone = phone.replace(" ", "").replace("-", "")

        if not cleaned_phone.lstrip("+").isdigit():
            raise forms.ValidationError(
                "A phone number can only contain digits, spaces, hyphens, and the ‘+’ sign."
            )

        if len(cleaned_phone) < 9:
            raise forms.ValidationError("The phone number is too short.")

        return phone
