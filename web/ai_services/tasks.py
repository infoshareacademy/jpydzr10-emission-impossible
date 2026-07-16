import logging

from celery import shared_task

from .models import AIChatMessage, AIChatSession
from .SLM_conf import BielikESGService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_ai_chat_message(self, session_id: int, question: str) -> str:
    """
    Asynchroniczne zadanie odpytujące model LLM.
    Nie blokuje wątku serwera HTTP.
    """
    try:
        session = AIChatSession.objects.get(id=session_id)
        ai_service = BielikESGService()

        answer = ai_service.generate_response(session, question)

        if not answer.startswith("Wystąpił błąd") and not answer.startswith(
            "Silnik AI"
        ):
            AIChatMessage.objects.create(
                session=session, role=AIChatMessage.Role.ASSISTANT, content=answer
            )

        return answer
    except AIChatSession.DoesNotExist:
        logger.error(f"Sesja AI o ID {session_id} nie istnieje.")
        return "Błąd: Sesja wygasła."
    except Exception as e:
        logger.error(f"Błąd przetwarzania AI: {e}")
        return "Błąd weryfikacji zadania w tle."
