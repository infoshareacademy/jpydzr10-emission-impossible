from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from workflow.models import RecordComment

from core.models import UserPageView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            # 1. Ulubione skróty użytkownika
            context["favorite_shortcuts"] = UserPageView.objects.filter(
                user=self.request.user
            ).order_by("-visit_count")[:5]

            # 2. Oczekujące zadania (Odrzucone rekordy do poprawy)
            pending_tasks = []

            # Pobieramy nierozwiązane komentarze (możesz w przyszłości dodać filtr
            # po spółkach, do których konkretny user ma uprawnienia)
            unresolved_comments = RecordComment.objects.filter(
                is_resolved=False
            ).prefetch_related("content_object")

            for comment in unresolved_comments:
                record = comment.content_object
                if not record:
                    continue

                model_class = record.__class__
                model_name = model_class._meta.model_name
                app_label = model_class._meta.app_label

                # Generowanie linku do edycji rekordu (z uwzględnieniem Scope 1 i Scope 2)
                try:
                    if app_label == "emissions":
                        if model_name in [
                            "stationarycombustion",
                            "mobilecombustion",
                            "processemission",
                            "fugitiveemission",
                        ]:
                            edit_url = reverse(
                                f"emissions:{model_name}-edit",
                                kwargs={
                                    "company_id": record.company_id,
                                    "pk": record.pk,
                                },
                            )
                        else:
                            edit_url = reverse(
                                f"emissions:{model_name}_edit", kwargs={"pk": record.pk}
                            )
                    else:
                        edit_url = "#"
                except Exception:
                    edit_url = "#"

                pending_tasks.append(
                    {
                        "title": f"Odrzucono: {model_class._meta.verbose_name}",
                        "comment_text": comment.text,
                        "company_name": (
                            record.company.name
                            if hasattr(record, "company")
                            else "Brak danych"
                        ),
                        "model_name": str(record),
                        "edit_url": edit_url,
                    }
                )

            context["pending_tasks"] = pending_tasks

        else:
            context["favorite_shortcuts"] = None
            context["pending_tasks"] = []

        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"
