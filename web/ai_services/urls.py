from django.urls import path

from .views import AITaskStatusView, GlobalAIAssistantView

app_name = "ai_services"

urlpatterns = [
    # Czysty adres: /ai/assistant/
    path("assistant/", GlobalAIAssistantView.as_view(), name="global_assistant"),
    path("status/<str:task_id>/", AITaskStatusView.as_view(), name="task_status"),
]
