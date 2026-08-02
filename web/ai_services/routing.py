from django.urls import path

from .consumers import BielikChatConsumer

websocket_urlpatterns = [
    path("ws/ai/chat/", BielikChatConsumer.as_asgi()),
]