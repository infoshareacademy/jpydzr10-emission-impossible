import json

from celery.result import AsyncResult
from companies.models import Companies
from core.mixins import PageViewTrackerMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit

from .models import AIChatMessage, AIChatSession
from .tasks import process_ai_chat_message


class GlobalAIAssistantView(PageViewTrackerMixin, LoginRequiredMixin, TemplateView):
    template_name = "ai_services/global_chat.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == "admin" or user.is_superuser:
            context["companies"] = Companies.objects.all().order_by("name")
        else:
            context["companies"] = (
                Companies.objects.filter(
                    user_permissions__user=user, user_permissions__can_read=True
                )
                .distinct()
                .order_by("name")
            )

        return context

    @method_decorator(ratelimit(key="user", rate="5/m", method="POST", block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return JsonResponse(
                {"error": "Za dużo zapytań. Spróbuj za minutę."}, status=429
            )

        try:
            body = json.loads(request.body)
            question = body.get("question", "").strip()
            company_id = body.get("company_id")
            scope_type = body.get("scope_type", "ALL")
        except (json.JSONDecodeError, TypeError):
            return JsonResponse(
                {"error": "Błąd dekodowania danych żądania."}, status=400
            )

        if not question or len(question) > 500:
            return JsonResponse(
                {"error": "Zapytanie musi mieć od 1 do 500 znaków."}, status=400
            )

        if not company_id:
            return JsonResponse(
                {"error": "Wybierz podmiot z listy przed wysłaniem wiadomości."},
                status=400,
            )

        user = request.user

        if user.role == "admin" or user.is_superuser:
            company = Companies.objects.filter(id=company_id).first()
        else:
            company = (
                Companies.objects.filter(
                    id=company_id,
                    user_permissions__user=user,
                    user_permissions__can_read=True,
                )
                .distinct()
                .first()
            )

        if not company:
            return JsonResponse(
                {"error": "Brak uprawnień lub spółka nie istnieje."}, status=403
            )

        session, created = AIChatSession.objects.get_or_create(
            user=user, company=company, scope_type=scope_type, is_active=True
        )

        AIChatMessage.objects.create(
            session=session, role=AIChatMessage.Role.USER, content=question
        )

        task = process_ai_chat_message.delay(session.id, question)

        return JsonResponse({"task_id": task.id, "status": "processing"})


class AITaskStatusView(LoginRequiredMixin, View):
    """Lekki endpoint do odpytywania o status zadania w Celery."""

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)

        response_data = {
            "status": task_result.state,
            "answer": task_result.result if task_result.ready() else None,
        }
        return JsonResponse(response_data)