from django.urls import path

from . import views
from .views import RecordClarificationView

app_name = "workflow"

urlpatterns = [
    path("admin/review/", views.AdminEnvelopeListView.as_view(), name="admin_list"),
    path(
        "admin/review/<int:pk>/",
        views.AdminEnvelopeReviewDetailView.as_view(),
        name="admin_detail",
    ),
    path(
        "admin/review/<str:app_label>/<str:model_name>/<int:pk>/action/",
        views.AdminReviewActionView.as_view(),
        name="record_action",
    ),
    path(
        "admin/review/<int:pk>/finalize/",
        views.AdminFinalizeReviewView.as_view(),
        name="finalize",
    ),
    path(
        "admin/clarify/<str:app_label>/<str:model_name>/<int:pk>/",
        RecordClarificationView.as_view(),
        name="record_clarify",
    ),
]
