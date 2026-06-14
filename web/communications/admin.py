from django.contrib import admin
from .models import Thread, Message


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ["subject", "company", "author", "category", "status", "created_at"]
    list_filter = ["company", "category", "status"]
    search_fields = ["subject", "company__name", "author__username"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["thread", "sender", "created_at"]
    list_filter = ["sender"]
    search_fields = ["thread__subject", "sender__username", "content"]

