from django.urls import path

from .views import (
    ReductionGoalCreateView,
    ReductionGoalDeleteView,
    ReductionGoalListView,
    ReductionGoalUpdateView,
    ReductionTargetCreateView,
    ReductionTargetDeleteView,
    ReductionTargetDetailView,
    ReductionTargetListView,
    ReductionTargetUpdateView,
    SimulationDashboardView,
)

app_name = "what_if"

urlpatterns = [
    path(
        "reduction-targets/",
        ReductionTargetListView.as_view(),
        name="reduction-target-list",
    ),
    path(
        "reduction-targets/add/",
        ReductionTargetCreateView.as_view(),
        name="reduction-target-add",
    ),
    path(
        "reduction-targets/<int:pk>/edit/",
        ReductionTargetUpdateView.as_view(),
        name="reduction-target-edit",
    ),
    path(
        "reduction-targets/<int:pk>/delete/",
        ReductionTargetDeleteView.as_view(),
        name="reduction-target-delete",
    ),
    path(
        "simulation/",
        SimulationDashboardView.as_view(),
        name="simulation",
    ),
    path(
        "reduction-targets/<int:pk>/",
        ReductionTargetDetailView.as_view(),
        name="reduction-target-detail",
    ),
    path("goals/", ReductionGoalListView.as_view(), name="goal_list"),
    path("goals/create/", ReductionGoalCreateView.as_view(), name="goal_create"),
    path("goals/<int:pk>/edit/", ReductionGoalUpdateView.as_view(), name="goal_edit"),
    path("goals/<int:pk>/delete/", ReductionGoalDeleteView.as_view(), name="goal_delete"),
]
