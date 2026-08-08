from core.models import CoreModel
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)
from encrypted_model_fields.fields import EncryptedCharField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name=_("Adres e-mail"))

    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name=_("Zdjęcie profilowe")
    )
    ROLE_CHOICES = [
        ("admin", _("Administrator")),
        ("użytkownik", _("Użytkownik")),
        ("audytor", _("Audytor")),
    ]
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="użytkownik", verbose_name=_("Rola")
    )
    companies = models.ManyToManyField(
        "companies.Companies",
        through="UserCompanyPermission",
        through_fields=("user", "company"),
        related_name="users",
        verbose_name=_("Firmy"),
    )

    class Meta:
        verbose_name = _("Użytkownik")
        verbose_name_plural = _("Użytkownicy")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserCompanyPermission(CoreModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="company_permissions",
        verbose_name=_("Użytkownik"),
    )
    company = models.ForeignKey(
        "companies.Companies",
        on_delete=models.CASCADE,
        related_name="user_permissions",
        verbose_name=_("Firma"),
    )
    can_save = models.BooleanField(default=False, verbose_name=_("Może zapisywać?"))
    can_read = models.BooleanField(default=True, verbose_name=_("Może przeglądać?"))

    class Meta:
        verbose_name = _("Uprawnienie do firmy")
        verbose_name_plural = _("Uprawnienia do firm")
        unique_together = ["user", "company"]

    def __str__(self):
        return (
            f"{self.user.username} – {self.company} "
            f"(read={self.can_read}, save={self.can_save})"
        )


class TOTPDevice(CoreModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="totp_devices",
        verbose_name=_("Użytkownik"),
    )
    secret = EncryptedCharField(
        max_length=255,
        verbose_name=_("Zaszyfrowany sekret TOTP"),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Aktywne 2FA"),
    )
    name = models.CharField(
        max_length=100,
        default="Default",
        verbose_name=_("Nazwa urządzenia"),
        blank=True,
    )
    confirmed = models.BooleanField(
        default=False,
        verbose_name=_("Potwierdzone"),
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Ostatnio użyte"),
    )

    class Meta:
        verbose_name = _("Urządzenie TOTP")
        verbose_name_plural = _("Urządzenia TOTP")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_user_device_name"
            )
        ]

    def __str__(self):
        return f"TOTP dla {self.user.username} ({self.name})"

    def verify_token(self, token: str) -> bool:
        """Tu wrzucisz logikę weryfikacji TOTP (pyotp.TOTP)"""
        pass