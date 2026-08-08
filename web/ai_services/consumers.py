import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from companies.models import Companies
from django.utils.translation import gettext as _  # <--- KLUCZOWY IMPORT DLA TŁUMACZEŃ

from .models import AIChatMessage, AIChatSession
from .SLM_conf import BielikESGService

logger = logging.getLogger(__name__)


class BielikChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            question = data.get("question", "").strip()
            company_id = data.get("company_id")
            scope_type = data.get("scope_type", "ALL")
        except json.JSONDecodeError:
            await self.send_error(_("Błąd dekodowania danych żądania."))
            return

        if not question or len(question) > 500:
            await self.send_error(_("Zapytanie musi mieć od 1 do 500 znaków."))
            return

        if not company_id:
            await self.send_error(_("Wybierz podmiot z listy przed wysłaniem wiadomości."))
            return

        company = await self.get_company(company_id)
        if not company:
            await self.send_error(_("Brak uprawnień lub spółka nie istnieje."))
            return

        session = await self.get_or_create_session(company, scope_type)
        await self.save_message(session, AIChatMessage.Role.USER, question)

        await self.send(
            text_data=json.dumps({"type": "status", "status": "processing"})
        )

        answer = await sync_to_async(self.generate_ai_response, thread_sensitive=False)(
            session, question
        )

        # Zapis i odesłanie odpowiedzi
        if not answer.startswith("Wystąpił błąd") and not answer.startswith(
            "Silnik AI"
        ):
            await self.save_message(session, AIChatMessage.Role.ASSISTANT, answer)

        await self.send(
            text_data=json.dumps(
                {"type": "message", "role": "assistant", "content": answer}
            )
        )

    async def send_error(self, message):
        await self.send(text_data=json.dumps({"type": "error", "message": message}))

    @sync_to_async
    def get_company(self, company_id):
        if self.user.role == "admin" or self.user.is_superuser:
            return Companies.objects.filter(id=company_id).first()
        return (
            Companies.objects.filter(
                id=company_id,
                user_permissions__user=self.user,
                user_permissions__can_read=True,
            )
            .distinct()
            .first()
        )

    @sync_to_async
    def get_or_create_session(self, company, scope_type):
        session, _ = AIChatSession.objects.get_or_create(
            user=self.user, company=company, scope_type=scope_type, is_active=True
        )
        return session

    @sync_to_async
    def save_message(self, session, role, content):
        return AIChatMessage.objects.create(session=session, role=role, content=content)

    def generate_ai_response(self, session, question):
        ai_service = BielikESGService()
        return ai_service.generate_response(session, question)