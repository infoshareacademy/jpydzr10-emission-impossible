from decimal import Decimal

from calculator.models import FuelType
from companies.models import Companies, Countries
from core.models import CoreModel
from django.db import models
from django.utils.translation import gettext_lazy as _

# Modele abstrakcyjne — nie tworzą tabel w bazie
# służą jako baza dla innych modeli


class BaseRecord(CoreModel):
    year = models.IntegerField()
    company = models.ForeignKey(
        Companies, on_delete=models.CASCADE, related_name="%(class)s_records"
    )
    data_quality = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True


class RecordStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Roboczy")
    PENDING = "PENDING", _("Do akceptacji")
    APPROVED = "APPROVED", _("Zatwierdzony")
    VERIFIED = "VERIFIED", _("Zweryfikowany")
    REJECTED = "REJECTED", _("Odrzucony")


class ActivityRecord(BaseRecord):
    amount = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=20)
    source = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=RecordStatus.choices,
        default=RecordStatus.DRAFT,
        verbose_name=_("Status"),
    )
    emission_tco2eq = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_("Emisja zadeklarowana"),
    )

    calculated_emission_tco2eq = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_("Emisja (Wyliczona przez system)"),
    )

    applied_factor_value = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        null=True,
        blank=True,
        verbose_name=_("Użyty wskaźnik (Wartość)"),
    )
    applied_factor_unit = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Użyty wskaźnik (Jednostka)"),
    )

    applied_converter_value = models.DecimalField(
        max_digits=12,
        decimal_places=5,
        default=Decimal("1.00000"),
        verbose_name=_("Użyty przelicznik jednostek (Wartość)"),
    )
    applied_converter_unit = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default="",
        verbose_name=_("Użyty przelicznik jednostek (Jednostka)"),
    )

    class Meta:
        abstract = True


class StationaryCombustion(ActivityRecord):
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.PROTECT,
        related_name="stationary_combustions",
        verbose_name=_("Paliwo"),
    )
    installation = models.CharField(max_length=200)
    raport = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "tbl_stationary_combustion"
        verbose_name = "Spalanie stacjonarne"
        verbose_name_plural = "Spalanie stacjonarne"


class MobileCombustion(ActivityRecord):
    vehicle = models.CharField(max_length=200)
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.PROTECT,
        related_name="mobile_combustion",
        verbose_name=_("Paliwo"),
    )
    raport = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "tbl_mobile_combustion"
        verbose_name = "Spalanie mobilne"
        verbose_name_plural = "Spalanie mobilne"


class ProcessEmission(ActivityRecord):
    process = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    raport = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "tbl_process_emissions"
        verbose_name = "Emisja procesowa"
        verbose_name_plural = "Emisje procesowe"


class FugitiveEmission(ActivityRecord):
    installation = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    raport = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "tbl_fugitive_emissions"
        verbose_name = "Emisja niezorganizowana"
        verbose_name_plural = "Emisje niezorganizowane"


class EnergyConsumption(ActivityRecord):
    energy_source = models.CharField(max_length=100)
    energy_type = models.CharField(max_length=100)

    class Meta:
        db_table = "tbl_e_cons"
        verbose_name = "Zużycie energii"
        verbose_name_plural = "Zużycie energii"


class EnergyPurchased(ActivityRecord):
    energy_type = models.CharField(max_length=100)
    trader = models.CharField(max_length=200, blank=True, default="")
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))

    class Meta:
        db_table = "tbl_e_purc"
        verbose_name = "Zakupiona energia"
        verbose_name_plural = "Zakupiona energia"


class EnergyProduced(ActivityRecord):
    installation = models.CharField(max_length=200, blank=True, default="")
    energy_type = models.CharField(max_length=100)
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))

    class Meta:
        db_table = "tbl_e_prod"
        verbose_name = "Wyprodukowana energia"
        verbose_name_plural = "Wyprodukowana energia"


class EnergySold(ActivityRecord):
    energy_type = models.CharField(max_length=100)
    customer = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        db_table = "tbl_e_sold"
        verbose_name = "Sprzedana energia"
        verbose_name_plural = "Sprzedana energia"


class EmissionFactor(models.Model):
    factor_name = models.CharField(max_length=200)
    country = models.ForeignKey(
        Countries,
        on_delete=models.PROTECT,
        related_name="emission_factors",
        verbose_name=_("Kraj"),
    )
    year = models.PositiveIntegerField()
    factor = models.DecimalField(max_digits=12, decimal_places=5)
    unit_factor = models.CharField(max_length=50)
    source = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "tbl_factors"
        verbose_name = "Wskaźnik emisji"
        verbose_name_plural = "Wskaźniki emisji"


class EmailLog(models.Model):
    date = models.DateTimeField()
    sender = models.CharField(max_length=100)
    recipients = models.CharField(max_length=1000)
    company = models.CharField(max_length=200)
    table_name = models.CharField(max_length=200, blank=True, null=True)
    record_ids = models.CharField(max_length=500, blank=True, null=True)
    template_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=500)
    scope = models.CharField(max_length=10, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = "tbl_email_log"
        verbose_name = "Log email"
        verbose_name_plural = "Logi email"
