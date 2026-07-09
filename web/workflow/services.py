from accounts.models import UserCompanyPermission
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.urls import reverse

from workflow.models import WorkflowStatusMixin

from .models import CompanyReportEnvelope, RecordComment, Task


@transaction.atomic
def submit_company_report(envelope: CompanyReportEnvelope) -> None:
    """
    Zmienia status koperty na IN_REVIEW.
    Automatycznie wyszukuje wszystkie robocze (DRAFT) rekordy emisyjne
    tej spółki i zmienia ich status na oczekujące (PENDING).
    """
    envelope.status = CompanyReportEnvelope.Status.IN_REVIEW
    envelope.save(update_fields=["status"])

    for model in apps.get_models():
        if issubclass(model, WorkflowStatusMixin) and hasattr(model, "company"):
            model.objects.filter(
                company=envelope.company,
                workflow_status=WorkflowStatusMixin.RecordStatus.DRAFT,
            ).update(workflow_status=WorkflowStatusMixin.RecordStatus.PENDING)


@transaction.atomic
def review_single_record(
    record: WorkflowStatusMixin, is_approved: bool, reviewer, reason: str = ""
) -> None:
    """
    Zatwierdza lub odrzuca pojedynczy rekord.
    W przypadku odrzucenia wymaga podania powodu (tworzy RecordComment).
    """
    if is_approved:
        record.workflow_status = WorkflowStatusMixin.RecordStatus.APPROVED
        record.save(update_fields=["workflow_status"])
    else:
        if not reason:
            raise ValueError("Odrzucenie rekordu wymaga podania powodu (uwagi).")

        record.workflow_status = WorkflowStatusMixin.RecordStatus.REJECTED
        record.save(update_fields=["workflow_status"])
        ctype = ContentType.objects.get_for_model(record)
        RecordComment.objects.create(
            author=reviewer, content_type=ctype, object_id=record.pk, text=reason
        )


@transaction.atomic
def return_report_to_user(envelope: CompanyReportEnvelope) -> Task:
    """
    Zwraca raport do spółki, otwierając ponownie możliwość edycji
    i generuje nowe zadanie poprawy dla użytkowników.
    """
    envelope.status = CompanyReportEnvelope.Status.RETURNED
    envelope.save(update_fields=["status"])
    task = Task.objects.create(
        company=envelope.company,
        task_type=Task.TaskType.CORRECTION,
        title=f"Wymagana poprawa danych emisyjnych - Okres {envelope.period.year}",
        description="Administrator odrzucił część wprowadzonych danych. Zapoznaj się z uwagami podświetlonymi na czerwono w poszczególnych widokach.",
    )

    permitted_users = UserCompanyPermission.objects.filter(
        company=envelope.company
    ).values_list("user", flat=True)
    if permitted_users:
        task.assigned_to.add(*permitted_users)

    return task


@transaction.atomic
def finalize_envelope_review(envelope: CompanyReportEnvelope) -> str:
    """
    Sprawdza statusy wszystkich rekordów spółki dla danego okresu.
    - Jeśli są jakiekolwiek rekordy REJECTED -> cofa kopertę do RETURNED i tworzy Task.
    - Jeśli wszystkie rekordy są APPROVED -> zamyka kopertę jako APPROVED (twarda blokada).
    """
    has_rejected = False
    has_pending = False

    for model in apps.get_models():
        if issubclass(model, WorkflowStatusMixin) and hasattr(model, "company"):
            queryset = model.objects.filter(company=envelope.company)
            if hasattr(model, "year"):
                queryset = queryset.filter(year=envelope.period.year)
            elif hasattr(model, "date"):
                queryset = queryset.filter(date__year=envelope.period.year)

            if queryset.filter(
                workflow_status=WorkflowStatusMixin.RecordStatus.REJECTED
            ).exists():
                has_rejected = True
            if queryset.filter(
                workflow_status=WorkflowStatusMixin.RecordStatus.PENDING
            ).exists():
                has_pending = True

    if has_pending:
        raise ValueError(
            "Nie można sfinalizować weryfikacji, dopóki istnieją rekordy o statusie PENDING."
        )

    if has_rejected:
        return_report_to_user(envelope)
        return "RETURNED"
    else:
        envelope.status = CompanyReportEnvelope.Status.APPROVED
        envelope.save(update_fields=["status"])
        return "APPROVED"


@transaction.atomic
def request_record_clarification(
    record: WorkflowStatusMixin, admin_user, message: str, deadline: str = None
) -> Task:
    if not message.strip():
        raise ValueError("Uwaga nie może być pusta.")

    record.workflow_status = WorkflowStatusMixin.RecordStatus.REJECTED
    record.save(update_fields=["workflow_status"])
    ctype = ContentType.objects.get_for_model(record)
    RecordComment.objects.create(
        author=admin_user, content_type=ctype, object_id=record.pk, text=message
    )

    task_title = (
        f"Wymagane wyjaśnienie: {ctype.name.title()} dla spółki {record.company.name}"
    )
    task, created = Task.objects.get_or_create(
        company=record.company,
        task_type=Task.TaskType.CORRECTION,
        is_completed=False,
        defaults={
            "title": task_title,
            "description": "Administrator dodał uwagi do rekordu w celu ponownej weryfikacji.",
            "deadline": deadline or None,
        },
    )

    if not created and deadline:
        task.deadline = deadline
        task.save(update_fields=["deadline"])

    permitted_users_ids = list(
        UserCompanyPermission.objects.filter(company=record.company).values_list(
            "user_id", flat=True
        )
    )
    if permitted_users_ids:
        task.assigned_to.add(*permitted_users_ids)

    return task
