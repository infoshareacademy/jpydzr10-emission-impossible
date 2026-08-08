from core.models import CoreModel
from django.db import models
from django.db.models import RESTRICT
from django.utils.translation import (
    gettext_lazy as _,  # <--- KLUCZOWY IMPORT DLA MODELI
)


class CompaniesGroup(CoreModel):
    gk_name = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        verbose_name=_("Nazwa grupy kapitałowej"),
    )
    lvl_in_structure = models.IntegerField(verbose_name=_("Poziom w strukturze"))

    class Meta:
        verbose_name = _("Grupa kapitałowa")
        verbose_name_plural = _("Grupy kapitałowe")

    def __str__(self):
        return self.gk_name


class Countries(CoreModel):
    name = models.CharField(
        max_length=75,
        unique=True,
        blank=False,
        verbose_name=_("Nazwa kraju"),
    )
    code_alfa_2 = models.CharField(
        max_length=2,
        unique=True,
        blank=False,
        verbose_name=_("Kod Alfa-2"),
    )

    class Meta:
        verbose_name = _("Kraj")
        verbose_name_plural = _("Kraje")

    def __str__(self):
        return self.name


class Companies(CoreModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        verbose_name=_("Nazwa firmy"),
    )
    country = models.ForeignKey(
        Countries,
        on_delete=RESTRICT,
        related_name="countries",
        related_query_name="country",
        verbose_name=_("Kraj"),
    )
    city = models.CharField(
        max_length=100,
        verbose_name=_("Miasto"),
        blank=False,
    )
    street = models.CharField(
        max_length=200,
        verbose_name=_("Ulica"),
        blank=True,
    )
    zip = models.CharField(
        max_length=20,
        verbose_name=_("Kod pocztowy"),
        blank=False,
    )
    phone = models.CharField(
        max_length=30,
        verbose_name=_("Numer telefonu"),
        blank=True,
    )
    mail = models.EmailField(
        verbose_name=_("Adres e-mail"),
        blank=True,
    )
    krs = models.PositiveIntegerField(
        verbose_name=_("Numer KRS"),
        unique=True,
    )
    regon = models.PositiveIntegerField(
        verbose_name=_("Numer REGON"),
        unique=True,
    )
    nip = models.CharField(
        max_length=10,
        verbose_name=_("NIP"),
        unique=True,
    )
    capital_group_name = models.ForeignKey(
        CompaniesGroup,
        on_delete=models.PROTECT,
        related_name="companies",
        related_query_name="company",
        verbose_name=_("Grupa kapitałowa"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Czy spółka aktywna"),
        help_text=_("Jeśli odznaczone, spółka nie będzie uwzględniana w procesach raportowania."),
        db_index=True,
    )

    class Meta:
        verbose_name = _("Spółka")
        verbose_name_plural = _("Spółki")

    def __str__(self):
        return self.name