from core.models import CoreModel
from django.db import models


class FuelType(CoreModel):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20)  # liquid, gas, solid

    def __str__(self):
        return self.name


class Supplier(CoreModel):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class FuelSpec(CoreModel):
    fuel_type = models.ForeignKey(
        FuelType,
        on_delete=models.CASCADE,
        blank=False,
        related_name="specs",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="fuel_specs",
    )

    density_kg_per_m3 = models.FloatField(null=True)
    calorific_mj_per_kg = models.FloatField(null=True)
    calorific_mj_per_m3 = models.FloatField(null=True)

    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fuel_type", "supplier"], name="unique_spec_per_fuel_supplier"
            ),
            models.UniqueConstraint(
                fields=["fuel_type"],
                condition=models.Q(supplier__isnull=True) & models.Q(is_default=True),
                name="unique_default_spec_per_fuel",
            ),
        ]

    def __str__(self):
        supplier_name = self.supplier.name if self.supplier else "DOMYŚLNY"
        return f"{self.fuel_type.name} ({supplier_name})"
