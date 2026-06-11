from django.urls import path

from .views import GlobalAIAssistantView

app_name = "ai_services"

urlpatterns = [
    # Czysty adres: /ai/assistant/
    path("assistant/", GlobalAIAssistantView.as_view(), name="global_assistant"),
]
