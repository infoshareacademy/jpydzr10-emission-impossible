from companies.models import Companies
from django.db import models


# Create your models here.
class ReductionTarget(models.Model):
    SCOPE_CHOICES = [
        ("Scope 1", "Zakres 1 (Emisje bezpośrednie)"),
        ("Scope 2", "Zakres 2 (Emisje pośrednie energetyczne)"),
        # ("Scope 3", "Zakres 3 (Inne emisje pośrednie)"),
        ("1+2", "Zakres 1 + Zakres 2"),
        # ("1+2+3", "Wszystkie zakresy (1+2+3)"),
    ]
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
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default="1+2",
        verbose_name="Zakres (Scope)",
    )

    class Meta:
        db_table = "tbl_reduction_targets"
        verbose_name = "Cel redukcji"
        verbose_name_plural = "Cele redukcji"

    def __str__(self):
        return f"{self.target_name} ({self.company.name})"
