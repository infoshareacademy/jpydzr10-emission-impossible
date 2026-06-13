from companies.models import Companies
from core.models import CoreModel
from django.conf import settings
from django.db import models


class Thread(CoreModel):
    STATUS_CHOICES = [
        ("open", "Otwarte"),
        ("closed", "Rozwiązane"),
    ]

    CATEGORY_CHOICES = [
        ("weryfikacja", "Weryfikacja danych"),
        ("korekta", "Korekta danych"),
        ("brak_danych", "Brakujące dane"),
        ("odchylenie", "Wyjaśnienie odchylenia"),
        ("dane_zrodlowe", "Dane źródłowe"),
        ("wlasna", "Własna wiadomość"),
    ]

    subject = models.CharField(max_length=255, verbose_name="Temat")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="wlasna",
        verbose_name="Kategoria",
    )
    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        related_name="threads",
        verbose_name="Spółka",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_threads",
        verbose_name="Autor",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="Status"
    )

    class Meta:
        verbose_name = "Communication thread"
        verbose_name_plural = "Communication threads"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.company.name})"


class Message(CoreModel):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages", verbose_name="Wątek"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Nadawca"
    )
    content = models.TextField(verbose_name="Treść wiadomości")

    class Meta:
        verbose_name = "messenger"
        verbose_name_plural = "messengers"
        ordering = ["created_at"]

    def __str__(self):
        return f"Odp: {self.thread.subject} od {self.sender.username}"
