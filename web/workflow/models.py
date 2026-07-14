from companies.models import Companies
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ReportingPeriod(models.Model):
    year = models.PositiveIntegerField(unique=True)
    is_active = models.BooleanField(default=False)
    deadline = models.DateField()

    class Meta:
        db_table = "workflow_reporting_period"

    def __str__(self):
        status = " (Aktywny)" if self.is_active else ""
        return f"Okres raportowy: {self.year}{status}"


class CompanyReportEnvelope(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Otwarte do wprowadzania"
        IN_REVIEW = "IN_REVIEW", "W weryfikacji przez Admina (zablokowane dla usera)"
        RETURNED = "RETURNED", "Zwrócone do poprawy (odblokowane)"
        APPROVED = "APPROVED", "Zatwierdzone (całkowita blokada)"

    period = models.ForeignKey(ReportingPeriod, on_delete=models.CASCADE)
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )

    class Meta:
        db_table = "workflow_company_envelope"
        unique_together = ("period", "company")

    def __str__(self):
        return f"{self.company} | {self.period.year} - {self.get_status_display()}"


class WorkflowStatusMixin(models.Model):
    class RecordStatus(models.TextChoices):
        DRAFT = "DRAFT", "Roboczy"
        PENDING = "PENDING", "Oczekuje na akceptację"
        APPROVED = "APPROVED", "Zaakceptowany"
        REJECTED = "REJECTED", "Odrzucony"

    workflow_status = models.CharField(
        max_length=20,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        abstract = True

    @property
    def app_label(self):
        return self._meta.app_label

    @property
    def model_name(self):
        return self._meta.model_name


class RecordComment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

def __str__(self):
    truncated_text = f"{self.text[:30]}..." if len(self.text) > 30 else self.text
    resolved_mark = " [Rozwiązany]" if self.is_resolved else ""
    return f"{self.author} ({self.created_at.strftime('%Y-%m-%d')}): {truncated_text}{resolved_mark}"

class Task(models.Model):
    class TaskType(models.TextChoices):
        DATA_ENTRY = "DATA_ENTRY", "Wprowadzenie danych"
        CORRECTION = "CORRECTION", "Poprawa odrzuconych rekordów"
        UNLOCK_REQ = "UNLOCK_REQ", "Wniosek o odblokowanie"
        CUSTOM = "CUSTOM", "Zadanie Ad-Hoc"

    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        status_icon = "✅" if self.is_completed else "⏳"
        return f"{status_icon} {self.title} | {self.company}"
