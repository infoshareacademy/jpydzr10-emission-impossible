from django.urls import path

from . import views

app_name = "communications"

urlpatterns = [
    path("", views.ThreadListView.as_view(), name="thread_list"),
    path("new/", views.ThreadCreateView.as_view(), name="thread_create"),
    path("<int:pk>/", views.ThreadDetailView.as_view(), name="thread_detail"),
    path("<int:pk>/close/", views.ThreadCloseView.as_view(), name="thread_close"),
]
