from core.models import CoreModel
from django.db import models
from django.db.models import RESTRICT


class CompaniesGroup(CoreModel):
    gk_name = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
    )
    lvl_in_structure = models.IntegerField()

    def __str__(self):
        return self.gk_name


class Countries(CoreModel):
    name = models.CharField(
        max_length=75,
        unique=True,
        blank=False,
    )
    code_alfa_2 = models.CharField(
        max_length=2,
        unique=True,
        blank=False,
    )

    def __str__(self):
        return self.name


class Companies(CoreModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        verbose_name="Company name",
    )
    country = models.ForeignKey(
        Countries,
        on_delete=RESTRICT,
        related_name="countries",
        related_query_name="country",
        verbose_name="Country name",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="City name",
        blank=False,
    )
    street = models.CharField(
        max_length=200,
        verbose_name="Street name",
        blank=True,
    )
    zip = models.CharField(
        max_length=20,
        verbose_name="Zip code",
        blank=False,
    )
    phone = models.CharField(
        max_length=30,
        verbose_name="Phone number",
    )
    mail = models.EmailField(
        verbose_name="Email address",
    )
    krs = models.PositiveIntegerField(
        verbose_name="KRS number",
        unique=True,
    )
    regon = models.PositiveIntegerField(
        verbose_name="Regon number",
        unique=True,
    )
    nip = models.CharField(
        max_length=10,
        verbose_name="Nip code",
        unique=True,
    )
    capital_group_name = models.ForeignKey(
        CompaniesGroup,
        on_delete=models.PROTECT,
        related_name="companies",
        related_query_name="company",
    )

    def __str__(self):
        return self.name
