from companies.models import Companies
from django.db import models


# Create your models here.
class ReductionTarget(models.Model):
    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        related_name="reduction_targets",
        verbose_name="Firma",
    )
    target_name = models.CharField(max_length=300)
    base_year = models.PositiveIntegerField()
    target_year = models.PositiveIntegerField()
    reduction_pct = models.DecimalField(max_digits=5, decimal_places=2)
    scope = models.CharField(max_length=10, default="1+2")

    class Meta:
        db_table = "tbl_reduction_targets"
        verbose_name = "Cel redukcji"
        verbose_name_plural = "Cele redukcji"

    def __str__(self):
        return f"{self.target_name} ({self.company.name})"
