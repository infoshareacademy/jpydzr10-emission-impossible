from accounts.models import UserCompanyPermission
from companies.models import Companies
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext as _

from workflow.models import ReportingPeriod, WorkflowStatusMixin

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
            raise ValueError(_("Odrzucenie rekordu wymaga podania powodu (uwagi)."))

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
        title=_("Wymagana poprawa danych emisyjnych - Okres %(year)s") % {"year": envelope.period.year},
        description=_("Administrator odrzucił część wprowadzonych danych. Zapoznaj się z uwagami podświetlonymi na czerwono w poszczególnych widokach."),
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
            _("Nie można sfinalizować weryfikacji, dopóki istnieją rekordy o statusie PENDING.")
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
        raise ValueError(_("Uwaga nie może być pusta."))

    record.workflow_status = WorkflowStatusMixin.RecordStatus.REJECTED
    record.save(update_fields=["workflow_status"])
    ctype = ContentType.objects.get_for_model(record)
    RecordComment.objects.create(
        author=admin_user, content_type=ctype, object_id=record.pk, text=message
    )

    task_title = (
        _("Wymagane wyjaśnienie: %(type)s dla spółki %(company)s")
        % {"type": ctype.name.title(), "company": record.company.name}
    )
    task, created = Task.objects.get_or_create(
        company=record.company,
        task_type=Task.TaskType.CORRECTION,
        is_completed=False,
        defaults={
            "title": task_title,
            "description": _("Administrator dodał uwagi do rekordu w celu ponownej weryfikacji."),
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


@transaction.atomic
def bulk_approve_company_records(envelope: CompanyReportEnvelope) -> int:
    """
    Zbiorczo zatwierdza wszystkie rekordy spółki dla danego okresu.
    Zwraca liczbę zaktualizowanych rekordów.
    """
    if envelope.status == CompanyReportEnvelope.Status.APPROVED:
        raise ValueError(_("Raport jest już zatwierdzony."))

    count = 0
    for model in apps.get_models():
        if issubclass(model, WorkflowStatusMixin) and hasattr(model, "company"):
            queryset = model.objects.filter(
                company=envelope.company,
                workflow_status=WorkflowStatusMixin.RecordStatus.PENDING,
            )

            if hasattr(model, "year"):
                queryset = queryset.filter(year=envelope.period.year)
            elif hasattr(model, "date"):
                queryset = queryset.filter(date__year=envelope.period.year)

            count += queryset.update(
                workflow_status=WorkflowStatusMixin.RecordStatus.APPROVED
            )

    return count


@transaction.atomic
def generate_envelopes_and_tasks_for_period(period: ReportingPeriod) -> int:
    """
    Wydajna funkcja bulk-insert generująca koperty i zadania startowe
    dla wszystkich aktywnych spółek w systemie.
    """
    companies = Companies.objects.filter(is_active=True)
    existing_envelopes = set(
        CompanyReportEnvelope.objects.filter(period=period).values_list(
            "company_id", flat=True
        )
    )

    envelopes_to_create = []
    tasks_to_create = []

    task_title = _("Uruchomiono proces zbierania danych za okres %(year)s") % {"year": period.year}

    for company in companies:
        if company.id not in existing_envelopes:
            envelopes_to_create.append(
                CompanyReportEnvelope(
                    period=period,
                    company=company,
                    status=CompanyReportEnvelope.Status.OPEN,
                )
            )
            tasks_to_create.append(
                Task(
                    company=company,
                    task_type=Task.TaskType.DATA_ENTRY,
                    title=task_title,
                    description=_("Rozpoczęto nowy okres raportowy. Proszę o uzupełnienie danych emisyjnych za rok %(year)s do wskazanego terminu.") % {"year": period.year},
                    deadline=period.deadline,
                    is_completed=False,
                )
            )
    if not envelopes_to_create:
        return 0

    CompanyReportEnvelope.objects.bulk_create(envelopes_to_create)
    created_tasks = Task.objects.bulk_create(tasks_to_create)
    company_users_qs = UserCompanyPermission.objects.filter(
        company__in=companies
    ).values_list("company_id", "user_id")
    company_to_users = {}
    for cid, uid in company_users_qs:
        company_to_users.setdefault(cid, []).append(uid)

    for task in created_tasks:
        uids = company_to_users.get(task.company_id, [])
        if uids:
            task.assigned_to.add(*uids)

    return len(envelopes_to_create)

@transaction.atomic
def create_admin_task_for_pending_record(record: WorkflowStatusMixin) -> Task:
    """
    Tworzy zadanie (Task) dla administratorów weryfikujących rekord.
    Wywoływane automatycznie przy zmianie statusu rekordu na PENDING.
    """
    ctype = ContentType.objects.get_for_model(record)

    task_title = _("Weryfikacja rekordu: %(type)s | %(company)s") % {"type": ctype.name.title(), "company": record.company.name}

    task = Task.objects.create(
        company=record.company,
        task_type=Task.TaskType.CUSTOM,
        title=task_title,
        description=(
            _("Użytkownik zmienił status rekordu (ID: %(pk)s) na Oczekujący. Wymagana weryfikacja poprawności danych.")
            % {"pk": record.pk}
        ),
        is_completed=False,
    )

    User = get_user_model()
    admin_users_ids = User.objects.filter(is_staff=True, is_active=True).values_list(
        "id", flat=True
    )

    if admin_users_ids:
        task.assigned_to.add(*admin_users_ids)

    return task