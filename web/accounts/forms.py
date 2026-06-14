from django import forms

from accounts.models import CustomUser


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Potwierdź hasłem",
        widget=forms.PasswordInput(),
        help_text="Wprowadź swoje aktualne hasło, aby autoryzować całkowite usunięcie profilu.",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError(
                "Podane hasło autoryzacyjne jest nieprawidłowe."
            )
        return password


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number", "avatar"]
        labels = {
            "first_name": "Imię",
            "last_name": "Nazwisko",
            "email": "Adres e-mail",
            "phone_number": "Numer telefonu",
            "avatar": "Zdjęcie profilowe",
        }
        widgets = {
            "avatar": forms.FileInput(),
        }
        help_texts = {
            "email": "Wymagany poprawny format adresu do powiadomień systemowych.",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Adres e-mail nie może być pusty.")
        return email
