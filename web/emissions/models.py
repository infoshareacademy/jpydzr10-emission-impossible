from decimal import Decimal

from companies.models import Companies
from django.db import models

# Modele abstrakcyjne — nie tworzą tabel w bazie
# służą jako baza dla innych modeli


class BaseRecord(models.Model):
    year = models.IntegerField()
    company = models.ForeignKey(
        Companies, on_delete=models.CASCADE, related_name="%(class)s_records"
    )
    data_quality = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True  # ← brak tabeli w bazie!

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
    
    class Meta:
        abstract = True  # ← też abstrakcyjny!


class StationaryCombustion(ActivityRecord):
    fuel = models.CharField(max_length=100)
    installation = models.CharField(max_length=200)
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    raport = models.CharField(max_length=300, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "tbl_stationary_combustion"
        verbose_name = "Spalanie stacjonarne"
        verbose_name_plural = "Spalanie stacjonarne"


class MobileCombustion(ActivityRecord):
    vehicle = models.CharField(max_length=200)
    fuel = models.CharField(max_length=100)
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    raport = models.CharField(max_length=300, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "tbl_mobile_combustion"
        verbose_name = "Spalanie mobilne"
        verbose_name_plural = "Spalanie mobilne"


class ProcessEmission(ActivityRecord):
    process = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    raport = models.CharField(max_length=300, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "tbl_process_emissions"
        verbose_name = "Emisja procesowa"
        verbose_name_plural = "Emisje procesowe"


class FugitiveEmission(ActivityRecord):
    installation = models.CharField(max_length=200)
    product = models.CharField(max_length=200)
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    raport = models.CharField(max_length=300, blank=True, null=True)
    notes = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "tbl_fugitive_emissions"
        verbose_name = "Emisja niezorganizowana"
        verbose_name_plural = "Emisje niezorganizowane"


class EnergyConsumption(ActivityRecord):
    energy_source = models.CharField(max_length=100)
    energy_type = models.CharField(max_length=100)
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )

    class Meta:
        db_table = "tbl_e_cons"
        verbose_name = "Zużycie energii"
        verbose_name_plural = "Zużycie energii"


class EnergyPurchased(ActivityRecord):
    energy_type = models.CharField(max_length=100)
    trader = models.CharField(max_length=200, blank=True, default="")
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    emission_tco2eq = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )

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
    country = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    factor = models.DecimalField(max_digits=12, decimal_places=5)
    unit_factor = models.CharField(max_length=50)
    source = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "tbl_factors"
        verbose_name = "Wskaźnik emisji"
        verbose_name_plural = "Wskaźniki emisji"


class UnitConverter(models.Model):
    unit_from = models.CharField(max_length=20)
    unit_to = models.CharField(max_length=20)
    factor = models.DecimalField(max_digits=12, decimal_places=5)

    class Meta:
        db_table = "tbl_converters"
        verbose_name = "Przelicznik jednostek"
        verbose_name_plural = "Przeliczniki jednostek"


class ReductionTarget(models.Model):
    company = models.CharField(max_length=200)
    target_name = models.CharField(max_length=300)
    base_year = models.PositiveIntegerField()
    target_year = models.PositiveIntegerField()
    reduction_pct = models.DecimalField(max_digits=5, decimal_places=2)
    scope = models.CharField(max_length=10, default="1+2")
    notes = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "tbl_reduction_targets"
        verbose_name = "Cel redukcji"
        verbose_name_plural = "Cele redukcji"


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


class ChangeLog(models.Model):
    id_rejestr_zmian = models.AutoField(primary_key=True)
    login = models.CharField(max_length=100)
    date_change = models.DateTimeField()
    table_name = models.CharField(max_length=200)
    record_id = models.CharField(max_length=50)
    change_type = models.CharField(max_length=10)
    previous_data = models.TextField(blank=True, null=True)
    actual_data = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "tbl_change_log"
        verbose_name = "Log zmian"
        verbose_name_plural = "Logi zmian"
