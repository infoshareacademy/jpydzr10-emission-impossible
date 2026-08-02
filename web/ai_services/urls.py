from django.urls import path

from .views import GlobalAIAssistantView

app_name = "ai_services"

urlpatterns = [
    path("assistant/", GlobalAIAssistantView.as_view(), name="global_assistant"),
]
