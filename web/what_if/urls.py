from django.urls import path

from .views import (
    ReductionTargetCreateView,
    ReductionTargetDeleteView,
    ReductionTargetListView,
    ReductionTargetUpdateView,
)

app_name = "what_if"

urlpatterns = [
    path(
        "company/<int:company_id>/reduction-targets/",
        ReductionTargetListView.as_view(),
        name="reduction-target-list",
    ),
    path(
        "company/<int:company_id>/reduction-targets/add/",
        ReductionTargetCreateView.as_view(),
        name="reduction-target-add",
    ),
    path(
        "company/<int:company_id>/reduction-targets/<int:pk>/edit/",
        ReductionTargetUpdateView.as_view(),
        name="reduction-target-edit",
    ),
    path(
        "company/<int:company_id>/reduction-targets/<int:pk>/delete/",
        ReductionTargetDeleteView.as_view(),
        name="reduction-target-delete",
    ),
]
