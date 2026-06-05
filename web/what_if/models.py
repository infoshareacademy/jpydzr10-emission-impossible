from django.db import models

# Create your models here.
class ReductionTarget(models.Model):
    company = models.CharField(max_length=200)
    target_name = models.CharField(max_length=300)
    base_year = models.PositiveIntegerField()
    target_year = models.PositiveIntegerField()
    reduction_pct = models.DecimalField(max_digits=5, decimal_places=2)
    scope = models.CharField(max_length=10, default="1+2")

    class Meta:
        db_table = "tbl_reduction_targets"
        verbose_name = "Cel redukcji"
        verbose_name_plural = "Cele redukcji"