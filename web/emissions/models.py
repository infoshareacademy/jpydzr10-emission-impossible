from decimal import Decimal

from calculator.models import FuelType
from companies.models import Companies, Countries
from core.models import CoreModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from workflow.models import WorkflowStatusMixin

# Modele abstrakcyjne – nie tworzą tabel w bazie
# służą jako baza dla innych modeli


class BaseRecord(CoreModel):
    year = models.IntegerField(verbose_name=_("Rok"))
    company = models.ForeignKey(
        Companies, on_delete=models.CASCADE, related_name="%(class)s_records", verbose_name=_("Firma")
    )
    data_quality = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Jakość danych"))

    class Meta:
        abstract = True


class ActivityRecord(BaseRecord):
    amount = models.DecimalField(max_digits=12, decimal_places=3, verbose_name=_("Ilość"))
    unit = models.CharField(max_length=20, verbose_name=_("Jednostka"))
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Źródło danych"))
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


class StationaryCombustion(ActivityRecord, WorkflowStatusMixin):
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.PROTECT,
        related_name="stationary_combustions",
        verbose_name=_("Paliwo"),
    )
    installation = models.CharField(max_length=200, verbose_name=_("Instalacja"))
    raport = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Raport"))

    def __str__(self):
        return f"Spalanie: {self.fuel} ({self.amount} jednostek)"

    class Meta:
        db_table = "tbl_stationary_combustion"
        verbose_name = _("Spalanie stacjonarne")
        verbose_name_plural = _("Spalanie stacjonarne")


class MobileCombustion(ActivityRecord, WorkflowStatusMixin):
    vehicle = models.CharField(max_length=200, verbose_name=_("Pojazd"))
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.PROTECT,
        related_name="mobile_combustion",
        verbose_name=_("Paliwo"),
    )
    raport = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Raport"))

    class Meta:
        db_table = "tbl_mobile_combustion"
        verbose_name = _("Spalanie mobilne")
        verbose_name_plural = _("Spalanie mobilne")


class ProcessEmission(ActivityRecord, WorkflowStatusMixin):
    process = models.CharField(max_length=200, verbose_name=_("Proces"))
    product = models.CharField(max_length=200, verbose_name=_("Produkt"))
    raport = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Raport"))

    class Meta:
        db_table = "tbl_process_emissions"
        verbose_name = _("Emisja procesowa")
        verbose_name_plural = _("Emisje procesowe")


class FugitiveEmission(ActivityRecord, WorkflowStatusMixin):
    installation = models.CharField(max_length=200, verbose_name=_("Instalacja"))
    product = models.CharField(max_length=200, verbose_name=_("Produkt"))
    raport = models.CharField(max_length=300, blank=True, null=True, verbose_name=_("Raport"))

    class Meta:
        db_table = "tbl_fugitive_emissions"
        verbose_name = _("Emisja niezorganizowana")
        verbose_name_plural = _("Emisje niezorganizowane")


class EnergyConsumption(ActivityRecord, WorkflowStatusMixin):
    energy_source = models.CharField(max_length=100, verbose_name=_("Źródło energii"))
    energy_type = models.CharField(max_length=100, verbose_name=_("Typ energii"))

    class Meta:
        db_table = "tbl_e_cons"
        verbose_name = _("Zużycie energii")
        verbose_name_plural = _("Zużycie energii")

    def save(self, *args, **kwargs):
        from emissions.models import EmissionFactor

        factor_obj = EmissionFactor.objects.filter(
            year=self.year, country=self.company.country, factor_name=self.energy_type
        ).first()

        if factor_obj:
            self.emission_tco2eq = float(self.amount) * float(factor_obj.factor)
        else:
            self.emission_tco2eq = 0.0

        super().save(*args, **kwargs)


class EnergyPurchased(ActivityRecord, WorkflowStatusMixin):
    energy_type = models.CharField(max_length=100, verbose_name=_("Typ energii"))
    trader = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Dostawca"))
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"), verbose_name=_("Wskaźnik"))

    class Meta:
        db_table = "tbl_e_purc"
        verbose_name = _("Zakupiona energia")
        verbose_name_plural = _("Zakupiona energia")

    def save(self, *args, **kwargs):
        from emissions.models import EmissionFactor

        factor_obj = EmissionFactor.objects.filter(
            year=self.year,
            country=self.company.country,
            factor_name=self.energy_type
        ).first()

        if factor_obj and self.amount:
            self.emission_tco2eq = float(self.amount) * float(factor_obj.factor)
            self.factor = factor_obj.factor
        else:
            self.emission_tco2eq = 0.0

        super().save(*args, **kwargs)


class EnergyProduced(ActivityRecord, WorkflowStatusMixin):
    installation = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Instalacja"))
    energy_type = models.CharField(max_length=100, verbose_name=_("Typ energii"))
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"), verbose_name=_("Wskaźnik"))

    class Meta:
        db_table = "tbl_e_prod"
        verbose_name = _("Wyprodukowana energia")
        verbose_name_plural = _("Wyprodukowana energia")

    def save(self, *args, **kwargs):
        from emissions.models import EmissionFactor

        factor_obj = EmissionFactor.objects.filter(
            year=self.year,
            country=self.company.country,
            factor_name=self.energy_type
        ).first()

        if factor_obj and self.amount:
            self.emission_tco2eq = float(self.amount) * float(factor_obj.factor)
            self.factor = factor_obj.factor
        else:
            self.emission_tco2eq = 0.0

        super().save(*args, **kwargs)


class EnergySold(ActivityRecord, WorkflowStatusMixin):
    energy_type = models.CharField(max_length=100, verbose_name=_("Typ energii"))
    customer = models.CharField(max_length=200, blank=True, default="", verbose_name=_("Odbiorca"))
    factor = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"), verbose_name=_("Wskaźnik"))

    class Meta:
        db_table = "tbl_e_sold"
        verbose_name = _("Sprzedana energia")
        verbose_name_plural = _("Sprzedana energia")

    def save(self, *args, **kwargs):
        from emissions.models import EmissionFactor

        factor_obj = EmissionFactor.objects.filter(
            year=self.year,
            country=self.company.country,
            factor_name=self.energy_type
        ).first()

        if factor_obj and self.amount:
            self.emission_tco2eq = float(self.amount) * float(factor_obj.factor)
            self.factor = factor_obj.factor
        else:
            self.emission_tco2eq = 0.0

        super().save(*args, **kwargs)


class EmissionFactor(models.Model):
    factor_name = models.CharField(max_length=200, verbose_name=_("Nazwa wskaźnika"))
    country = models.ForeignKey(
        Countries,
        on_delete=models.PROTECT,
        related_name="emission_factors",
        verbose_name=_("Kraj"),
    )
    year = models.PositiveIntegerField(verbose_name=_("Rok"))
    factor = models.DecimalField(max_digits=12, decimal_places=5, verbose_name=_("Wartość wskaźnika"))
    unit_factor = models.CharField(max_length=50, verbose_name=_("Jednostka wskaźnika"))
    source = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Źródło danych"))

    class Meta:
        db_table = "tbl_factors"
        verbose_name = _("Wskaźnik emisji")
        verbose_name_plural = _("Wskaźniki emisji")


class EmailLog(models.Model):
    date = models.DateTimeField(verbose_name=_("Data"))
    sender = models.CharField(max_length=100, verbose_name=_("Nadawca"))
    recipients = models.CharField(max_length=1000, verbose_name=_("Odbiorcy"))
    company = models.CharField(max_length=200, verbose_name=_("Firma"))
    table_name = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Nazwa tabeli"))
    record_ids = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("ID rekordów"))
    template_type = models.CharField(max_length=50, verbose_name=_("Typ szablonu"))
    subject = models.CharField(max_length=500, verbose_name=_("Temat"))
    scope = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Zakres"))
    year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Rok"))

    class Meta:
        db_table = "tbl_email_log"
        verbose_name = _("Log email")
        verbose_name_plural = _("Logi email")