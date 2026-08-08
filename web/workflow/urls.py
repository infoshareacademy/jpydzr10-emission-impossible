from django.urls import path

from .views import (
    AdminBulkApproveView,
    AdminDashboardView,
    AdminEnvelopeListView,
    AdminEnvelopeReviewDetailView,
    AdminFinalizeReviewView,
    AdminReviewActionView,
    RecordClarificationView,
    ReportingPeriodCreateView,
    ReportingPeriodListView,
)

app_name = "workflow"

urlpatterns = [
    path("periods/", ReportingPeriodListView.as_view(), name="period_list"),
    path("periods/create/", ReportingPeriodCreateView.as_view(), name="period_create"),
    path("admin/envelopes/", AdminEnvelopeListView.as_view(), name="admin_list"),
    path(
        "admin/envelope/<int:pk>/",
        AdminEnvelopeReviewDetailView.as_view(),
        name="admin_detail",
    ),
    path(
        "admin/envelope/<int:envelope_id>/bulk-approve/",
        AdminBulkApproveView.as_view(),
        name="bulk_approve",
    ),
    path(
        "admin/review/<str:app_label>/<str:model_name>/<int:pk>/action/",
        AdminReviewActionView.as_view(),
        name="review_action",
    ),
    path(
        "admin/review/<int:pk>/finalize/",
        AdminFinalizeReviewView.as_view(),
        name="finalize_review",
    ),
    path(
        "admin/review/<str:app_label>/<str:model_name>/<int:pk>/clarify/",
        RecordClarificationView.as_view(),
        name="record_clarify",
    ),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),
]
