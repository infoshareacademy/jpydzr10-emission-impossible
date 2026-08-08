from companies.models import Companies
from core.models import CoreModel
from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class Thread(CoreModel):
    STATUS_CHOICES = [
        ("open", _("Otwarte")),
        ("closed", _("Rozwiązane")),
    ]

    CATEGORY_CHOICES = [
        ("weryfikacja", _("Weryfikacja danych")),
        ("korekta", _("Korekta danych")),
        ("brak_danych", _("Brakujące dane")),
        ("odchylenie", _("Wyjaśnienie odchylenia")),
        ("dane_zrodlowe", _("Dane źródłowe")),
        ("wlasna", _("Własna wiadomość")),
    ]

    subject = models.CharField(max_length=255, verbose_name=_("Temat"))
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="wlasna",
        verbose_name=_("Kategoria"),
    )
    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        related_name="threads",
        verbose_name=_("Spółka"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_threads",
        verbose_name=_("Autor"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", verbose_name=_("Status")
    )

    class Meta:
        verbose_name = _("Wątek komunikacyjny")
        verbose_name_plural = _("Wątki komunikacyjne")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.company.name})"


class Message(CoreModel):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages", verbose_name=_("Wątek")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Nadawca")
    )
    content = models.TextField(verbose_name=_("Treść wiadomości"))

    class Meta:
        verbose_name = _("Wiadomość")
        verbose_name_plural = _("Wiadomości")
        ordering = ["created_at"]

    def __str__(self):
        return f"Odp: {self.thread.subject} od {self.sender.username}"