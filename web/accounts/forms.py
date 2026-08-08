from django import forms
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA FORMULARZY
)

from accounts.models import CustomUser


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label=_("Potwierdź hasłem"),
        widget=forms.PasswordInput(),
        help_text=_("Wprowadź swoje aktualne hasło, aby autoryzować całkowite usunięcie profilu."),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("Podane hasło autoryzacyjne jest nieprawidłowe.")
            )
        return password


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number", "avatar"]
        labels = {
            "first_name": _("Imię"),
            "last_name": _("Nazwisko"),
            "email": _("Adres e-mail"),
            "phone_number": _("Numer telefonu"),
            "avatar": _("Zdjęcie profilowe"),
        }
        widgets = {
            "avatar": forms.FileInput(),
        }
        help_texts = {
            "email": _("Wymagany poprawny format adresu do powiadomień systemowych."),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(_("Adres e-mail nie może być pusty."))
        return email