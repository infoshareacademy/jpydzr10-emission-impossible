from companies.models import Companies
from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class AIChatSession(models.Model):
    """
    Model reprezentujący pojedynczą sesję/wątek rozmowy z Asystentem AI.
    """

    SCOPE_CHOICES = [
        ("ALL", _("Cały Ślad Węglowy")),
        ("Z1", _("Zakres 1")),
        ("Z2", _("Zakres 2")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
        verbose_name=_("Użytkownik"),
    )
    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        related_name="ai_sessions",
        verbose_name=_("Analizowana Spółka"),
    )
    scope_type = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default="ALL",
        verbose_name=_("Zakres merytoryczny"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Sesja aktywna"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data utworzenia"))

    class Meta:
        db_table = "tbl_ai_chat_sessions"
        verbose_name = _("Sesja Czatu AI")
        verbose_name_plural = _("Sesje Czatu AI")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sesja #{self.id} | {self.user.username} | {self.company.name}"


class AIChatMessage(models.Model):
    """
    Model reprezentujący pojedynczą wiadomość (prompt użytkownika lub odpowiedź modelu) w ramach sesji.
    """

    class Role(models.TextChoices):
        USER = "user", _("Użytkownik")
        ASSISTANT = "assistant", _("Asystent AI")
        SYSTEM = "system", _("System / Kontekst")

    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Sesja"),
    )
    role = models.CharField(max_length=20, choices=Role.choices, verbose_name=_("Rola"))
    content = models.TextField(verbose_name=_("Treść wiadomości"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data utworzenia"))

    class Meta:
        db_table = "tbl_ai_chat_messages"
        verbose_name = _("Wiadomość AI")
        verbose_name_plural = _("Wiadomości AI")
        ordering = [
            "created_at"
        ]  # Sortowanie chronologiczne, aby poprawnie odtwarzać historię

    def __str__(self):
        return (
            f"{self.get_role_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
        )