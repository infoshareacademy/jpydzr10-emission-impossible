from django import template
from django.apps import apps
from django.urls import reverse

from workflow.models import WorkflowStatusMixin

register = template.Library()


@register.simple_tag
def get_grouped_rejected_records(task):
    """
    Skanuje wszystkie modele emisji w poszukiwaniu odrzuconych rekordów
    dla spółki przypisanej do Taska i grupuje je na potrzeby interfejsu.
    """
    if task.task_type != "CORRECTION":
        return {}

    grouped = {}
    for model in apps.get_models():
        if issubclass(model, WorkflowStatusMixin) and hasattr(model, "company"):
            records = model.objects.filter(
                company=task.company,
                workflow_status=WorkflowStatusMixin.RecordStatus.REJECTED,
            )
            count = records.count()
            if count > 0:
                v_name = model._meta.verbose_name.title()

                try:
                    list_url = reverse(
                        f"emissions:{model._meta.model_name}-list",
                        kwargs={"company_id": task.company_id},
                    )
                except:
                    list_url = "#"

                items = []
                for r in records:
                    try:
                        edit_url = reverse(
                            f"emissions:{model._meta.model_name}-edit",
                            kwargs={"company_id": r.company_id, "pk": r.pk},
                        )
                    except:
                        edit_url = "#"
                    items.append({"id": r.pk, "str": str(r), "edit_url": edit_url})

                grouped[v_name] = {"count": count, "list_url": list_url, "items": items}

    return grouped
