from core.models import CoreModel
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class FuelType(CoreModel):
    name = models.CharField(max_length=50, verbose_name=_("Nazwa typu paliwa"))
    symbol = models.CharField(max_length=20, unique=True, verbose_name=_("Symbol"))
    category = models.CharField(max_length=20, verbose_name=_("Kategoria"))  # liquid, gas, solid

    class Meta:
        verbose_name = _("Typ paliwa")
        verbose_name_plural = _("Typy paliw")

    def __str__(self):
        return self.name


class Supplier(CoreModel):
    name = models.CharField(max_length=128, verbose_name=_("Nazwa dostawcy"))

    class Meta:
        verbose_name = _("Dostawca")
        verbose_name_plural = _("Dostawcy")

    def __str__(self):
        return self.name


class FuelSpec(CoreModel):
    fuel_type = models.ForeignKey(
        FuelType,
        on_delete=models.CASCADE,
        blank=False,
        related_name="specs",
        verbose_name=_("Typ paliwa"),
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="fuel_specs",
        verbose_name=_("Dostawca"),
    )

    density_kg_per_m3 = models.FloatField(null=True, verbose_name=_("Gęstość (kg/m³)"))
    calorific_mj_per_kg = models.FloatField(null=True, verbose_name=_("Wartość opałowa (MJ/kg)"))
    calorific_mj_per_m3 = models.FloatField(null=True, verbose_name=_("Wartość opałowa (MJ/m³)"))

    is_default = models.BooleanField(default=False, verbose_name=_("Domyślny"))

    class Meta:
        verbose_name = _("Specyfikacja paliwa")
        verbose_name_plural = _("Specyfikacje paliw")
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
        supplier_name = self.supplier.name if self.supplier else str(_("DOMYŚLNY"))
        return f"{self.fuel_type.name} ({supplier_name})"