from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import CoreModel
from encrypted_model_fields.fields import EncryptedCharField
from django.db import models


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("użytkownik", "Użytkownik"),
        ("audytor", "Audytor"),
    ]
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="użytkownik", verbose_name="Rola"
    )
    companies = models.ManyToManyField(
        "companies.Companies",
        through="UserCompanyPermission",
        through_fields=("user", "company"),
        related_name="users",
        verbose_name="Firmy",
    )

    class Meta:
        verbose_name = "Użytkownik"
        verbose_name_plural = "Użytkownicy"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserCompanyPermission(CoreModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="company_permissions",
        verbose_name="Użytkownik",
    )
    company = models.ForeignKey(
        "companies.Companies",
        on_delete=models.CASCADE,
        related_name="user_permissions",
        verbose_name="Firma",
    )
    can_save = models.BooleanField(default=False, verbose_name="Może zapisywać?")
    can_read = models.BooleanField(default=True, verbose_name="Może przeglądać?")

    class Meta:
        verbose_name = "Uprawnienie do firmy"
        verbose_name_plural = "Uprawnienia do firm"
        unique_together = ["user", "company"]

    def __str__(self):
        return (
            f"{self.user.username} → {self.company} "
            f"(read={self.can_read}, save={self.can_save})"
        )

class TOTPDevice(CoreModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="totp_devices",
        verbose_name="Użytkownik",
    )
    secret = EncryptedCharField(
        max_length=255,
        verbose_name="Zaszyfrowany sekret TOTP",
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Aktywne 2FA",
    )
    name = models.CharField(
        max_length=100,
        default="Default",
        verbose_name="Nazwa urządzenia",
        blank=True,
    )
    confirmed = models.BooleanField(
        default=False,
        verbose_name="Potwierdzone",
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ostatnio użyte",
    )

    class Meta:
        verbose_name = "Urządzenie TOTP"
        verbose_name_plural = "Urządzenia TOTP"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_user_device_name'
            )
        ]

    def __str__(self):
        return f"TOTP dla {self.user.username} ({self.name})"

    def verify_token(self, token: str) -> bool:
        """Tu wrzucisz logikę weryfikacji TOTP (pyotp.TOTP)"""
        pass