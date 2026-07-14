from companies.models import Companies
from django.db import models


class ReductionGoal(models.Model):

    SCOPE_CHOICES = [
        ("Scope 1", "Zakres 1 (Emisje bezpośrednie)"),
        ("Scope 2", "Zakres 2 (Emisje pośrednie energetyczne)"),
        ("1+2", "Zakres 1 + Zakres 2"),
    ]
    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dedicated_goals",
        verbose_name="Dedykowana spółka (zostaw puste = cel globalny)",
        help_text="Jeśli wybierzesz spółkę, cel będzie widoczny tylko dla niej.",
    )
    name = models.CharField(max_length=300, verbose_name="Nazwa celu")
    base_year = models.PositiveIntegerField(verbose_name="Rok bazowy")
    target_year = models.PositiveIntegerField(verbose_name="Rok docelowy")
    reduction_pct = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Docelowa redukcja (%)"
    )
    scope = models.CharField(
        max_length=10,
        choices=SCOPE_CHOICES,
        default="1+2",
        verbose_name="Zakres (Scope)",
    )

    class Meta:
        db_table = "tbl_reduction_goals"
        verbose_name = "Cel redukcji (Globalny)"
        verbose_name_plural = "Cele redukcji (Globalne)"

    def __str__(self) -> str:
        prefix = f"[{self.company.name}] " if self.company_id else "[GLOBALNY] "
        return f"{prefix}{self.name} ({self.reduction_pct}%)"


class ReductionTarget(models.Model):

    company = models.ForeignKey(
        Companies,
        on_delete=models.CASCADE,
        related_name="reduction_targets",
        verbose_name="Firma",
    )
    goal = models.ForeignKey(
        ReductionGoal,
        on_delete=models.CASCADE,
        related_name="company_targets",
        verbose_name="Przypisany cel",
    )

    class Meta:
        db_table = "tbl_reduction_targets"
        verbose_name = "Przypisanie celu"
        verbose_name_plural = "Przypisania celów"
        unique_together = ("company", "goal")

    def __str__(self) -> str:
        return f"{self.target_name} ({self.company.name})"

    @property
    def target_name(self) -> str:
        return self.goal.name if self.goal_id else ""

    @property
    def base_year(self) -> int:
        return self.goal.base_year if self.goal_id else 0

    @property
    def target_year(self) -> int:
        return self.goal.target_year if self.goal_id else 0

    @property
    def reduction_pct(self):
        return self.goal.reduction_pct if self.goal_id else 0

    @property
    def scope(self) -> str:
        return self.goal.scope if self.goal_id else ""
