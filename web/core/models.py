from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class CoreModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data utworzenia"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("Utworzył(-a)"),
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Data aktualizacji"))
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("Zaktualizował(-a)"),
    )
    note = models.TextField(blank=True, verbose_name=_("Notatka"))

    class Meta:
        abstract = True


class UserPageView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_views", verbose_name=_("Użytkownik")
    )
    view_name = models.CharField(max_length=255, verbose_name=_("Nazwa widoku"))
    url_path = models.CharField(max_length=255, verbose_name=_("Ścieżka URL"))
    visit_count = models.PositiveIntegerField(default=1, verbose_name=_("Liczba odwiedzin"))
    last_visited = models.DateTimeField(auto_now=True, verbose_name=_("Ostatnio odwiedzone"))

    class Meta:
        db_table = "user_page_views"
        verbose_name = _("Wyświetlenie strony użytkownika")
        verbose_name_plural = _("Wyświetlenia stron użytkowników")
        unique_together = ("user", "view_name")
        indexes = [
            models.Index(fields=["user", "-visit_count"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.view_name} ({self.visit_count})"


class UserCarbonFootprint(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carbon_stats',
        verbose_name=_("Użytkownik"),
    )
    total_emissions_kg = models.FloatField(
        default=0.0,
        verbose_name=_("Całkowita emisja (kg CO2eq)"),
    )
    total_requests = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Całkowita liczba zapytań"),
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Ostatnia aktualizacja"),
    )

    class Meta:
        verbose_name = _("Ślad węglowy użytkownika")
        verbose_name_plural = _("Ślady węglowe użytkowników")

    def __str__(self):
        requests_label = _("zapytań")
        return (
            f'{self.user.username}: {self.total_emissions_kg:.6f} kg CO2eq '
            f'({self.total_requests} {requests_label})'
        )