from django.conf import settings
from django.db import models


class CoreModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )
    note = models.TextField(blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UserPageView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_views"
    )
    view_name = models.CharField(max_length=255)
    url_path = models.CharField(max_length=255)
    visit_count = models.PositiveIntegerField(default=1)
    last_visited = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_page_views"
        unique_together = ("user", "view_name")
        indexes = [
            models.Index(fields=["user", "-visit_count"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.view_name} ({self.visit_count})"


class UserCarbonFootprint(models.Model):
  user = models.OneToOneField(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE,
      related_name='carbon_stats',
  )
  total_emissions_kg = models.FloatField(
      default=0.0
  )
  total_requests = models.PositiveIntegerField(default=0)
  last_updated = models.DateTimeField(auto_now=True)

  def __str__(self):
    return (
        f'{self.user.username}: {self.total_emissions_kg:.6f} kg CO2eq'
        f' ({self.total_requests} zapytań)'
    )
