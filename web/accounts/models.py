from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import CoreModel


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Zdjęcie profilowe")
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