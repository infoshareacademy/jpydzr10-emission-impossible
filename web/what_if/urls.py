from django.urls import path

from .views import (
    ReductionTargetCreateView,
    ReductionTargetDeleteView,
    ReductionTargetListView,
    ReductionTargetUpdateView,
)

app_name = "what_if"

urlpatterns = [
    # Główna lista (teraz bez company_id w URL)
    path("reduction-targets/", ReductionTargetListView.as_view(), name="reduction-target-list"),
    path("reduction-targets/add/", ReductionTargetCreateView.as_view(), name="reduction-target-add"),
    path("reduction-targets/<int:pk>/edit/", ReductionTargetUpdateView.as_view(), name="reduction-target-edit"),
    path("reduction-targets/<int:pk>/delete/", ReductionTargetDeleteView.as_view(), name="reduction-target-delete"),
]