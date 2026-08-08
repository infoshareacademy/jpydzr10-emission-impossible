from companies.models import Companies
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class ReportingPeriod(models.Model):
    year = models.PositiveIntegerField(unique=True, verbose_name=_("Rok raportowy"))
    is_active = models.BooleanField(default=False, verbose_name=_("Aktywny"))
    deadline = models.DateField(verbose_name=_("Ostateczny termin"))

    class Meta:
        db_table = "workflow_reporting_period"
        verbose_name = _("Okres raportowy")
        verbose_name_plural = _("Okresy raportowe")

    def __str__(self):
        status = f" ({_('Aktywny')})" if self.is_active else ""
        return f"{_('Okres raportowy')}: {self.year}{status}"


class CompanyReportEnvelope(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", _("Otwarte do wprowadzania")
        IN_REVIEW = "IN_REVIEW", _("W weryfikacji przez Admina (zablokowane dla usera)")
        RETURNED = "RETURNED", _("Zwrócone do poprawy (odblokowane)")
        APPROVED = "APPROVED", _("Zatwierdzone (całkowita blokada)")

    period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE, verbose_name=_("Okres"))
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, verbose_name=_("Firma"))
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name=_("Status")
    )

    class Meta:
        db_table = "workflow_company_envelope"
        unique_together = ("period", "company")
        verbose_name = _("Koperta raportowa spółki")
        verbose_name_plural = _("Koperty raportowe spółek")

    def __str__(self):
        return f"{self.company} | {self.period.year} - {self.get_status_display()}"


class WorkflowStatusMixin(models.Model):
    class RecordStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Roboczy")
        PENDING = "PENDING", _("Oczekuje na akceptację")
        APPROVED = "APPROVED", _("Zaakceptowany")
        REJECTED = "REJECTED", _("Odrzucony")

    workflow_status = models.CharField(
        max_length=20,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
        verbose_name=_("Status workflow"),
    )

    class Meta:
        abstract = True

    @property
    def app_label(self):
        return self._meta.app_label

    @property
    def model_name(self):
        return self._meta.model_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_workflow_status = self.workflow_status

    def save(self, *args, **kwargs):
        status_changed_to_pending = (
            self.workflow_status == self.RecordStatus.PENDING
            and self._initial_workflow_status != self.RecordStatus.PENDING
        )

        super().save(*args, **kwargs)

        if status_changed_to_pending:
            from workflow.services import create_admin_task_for_pending_record

            create_admin_task_for_pending_record(self)

        self._initial_workflow_status = self.workflow_status


class RecordComment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Autor"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField(verbose_name=_("Treść"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data utworzenia"))
    is_resolved = models.BooleanField(default=False, verbose_name=_("Rozwiązany"))

    class Meta:
        verbose_name = _("Komentarz do rekordu")
        verbose_name_plural = _("Komentarze do rekordów")

    def __str__(self):
        truncated_text = f"{self.text[:30]}..." if len(self.text) > 30 else self.text
        resolved_mark = f" [{_('Rozwiązany')}]" if self.is_resolved else ""
        return f"{self.author} ({self.created_at.strftime('%Y-%m-%d')}): {truncated_text}{resolved_mark}"


class Task(models.Model):
    class TaskType(models.TextChoices):
        DATA_ENTRY = "DATA_ENTRY", _("Wprowadzenie danych")
        CORRECTION = "CORRECTION", _("Poprawa odrzuconych rekordów")
        UNLOCK_REQ = "UNLOCK_REQ", _("Wniosek o odblokowanie")
        CUSTOM = "CUSTOM", _("Zadanie Ad-Hoc")

    company = models.ForeignKey(Companies, on_delete=models.CASCADE, verbose_name=_("Firma"))
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name=_("Przypisany do"))
    task_type = models.CharField(max_length=20, choices=TaskType.choices, verbose_name=_("Typ zadania"))
    title = models.CharField(max_length=255, verbose_name=_("Tytuł"))
    description = models.TextField(blank=True, verbose_name=_("Opis"))
    deadline = models.DateField(null=True, blank=True, verbose_name=_("Termin"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Ukończone"))

    class Meta:
        verbose_name = _("Zadanie")
        verbose_name_plural = _("Zadania")

    def __str__(self):
        status_icon = "✓" if self.is_completed else "⏳"
        return f"{status_icon} {self.title} | {self.company}"