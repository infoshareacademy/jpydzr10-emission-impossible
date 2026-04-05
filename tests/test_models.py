"""
Testy walidacji modeli Pydantic.
Sprawdza poprawność tworzenia obiektów, walidatory pól i obsługę błędów.
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.application.class_models import (
    StationaryCombustion, MobileCombustion, FugitiveEmission, ProcessEmission,
    EnergyConsumption, EmissionFactor, UnitConverter, Company,
    UserAuthorization, UserPermission, MIN_YEAR, MAX_YEAR,
)


class TestStationaryCombustionModel:
    """Walidacja modelu spalania stacjonarnego."""

    def test_valid_record(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
        )
        assert r.fuel == "gaz ziemny"
        assert r.emission_tco2eq is None

    def test_invalid_fuel(self):
        with pytest.raises(ValidationError, match="Nieznany typ paliwa"):
            StationaryCombustion(
                id=1, year=2025, company="Test", amount=Decimal("100"),
                unit="m3", fuel="wodór", installation="piec",
            )

    def test_invalid_unit(self):
        with pytest.raises(ValidationError, match="Nieznana jednostka"):
            StationaryCombustion(
                id=1, year=2025, company="Test", amount=Decimal("100"),
                unit="baryłki", fuel="gaz ziemny", installation="piec",
            )

    def test_negative_amount(self):
        with pytest.raises(ValidationError):
            StationaryCombustion(
                id=1, year=2025, company="Test", amount=Decimal("-5"),
                unit="m3", fuel="gaz ziemny", installation="piec",
            )

    def test_year_too_low(self):
        with pytest.raises(ValidationError):
            StationaryCombustion(
                id=1, year=1990, company="Test", amount=Decimal("100"),
                unit="m3", fuel="gaz ziemny", installation="piec",
            )

    def test_year_too_high(self):
        with pytest.raises(ValidationError):
            StationaryCombustion(
                id=1, year=2099, company="Test", amount=Decimal("100"),
                unit="m3", fuel="gaz ziemny", installation="piec",
            )

    def test_empty_company(self):
        with pytest.raises(ValidationError):
            StationaryCombustion(
                id=1, year=2025, company="", amount=Decimal("100"),
                unit="m3", fuel="gaz ziemny", installation="piec",
            )

    def test_raport_string(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            emission_tco2eq=Decimal("10"), raport="KOBiZE",
        )
        assert r.raport == "KOBiZE"

    def test_raport_empty_is_none(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            raport="",
        )
        assert r.raport is None

    def test_emission_none_stays_none(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            emission_tco2eq=None,
        )
        assert r.emission_tco2eq is None

    def test_emission_empty_string_is_none(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            emission_tco2eq="",
        )
        assert r.emission_tco2eq is None

    def test_emission_with_value(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            emission_tco2eq=Decimal("25.5"),
        )
        assert r.emission_tco2eq == Decimal("25.5")

    def test_notes_optional(self):
        r = StationaryCombustion(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="m3", fuel="gaz ziemny", installation="piec",
            notes="test uwagi",
        )
        assert r.notes == "test uwagi"


class TestMobileCombustionModel:
    """Walidacja modelu spalania mobilnego."""

    def test_valid_record(self):
        r = MobileCombustion(
            id=1, year=2025, company="Test", amount=Decimal("2400"),
            unit="l", vehicle="samochód osobowy", fuel="benzyna",
        )
        assert r.vehicle == "samochód osobowy"
        assert r.emission_tco2eq is None

    def test_emission_and_raport(self):
        r = MobileCombustion(
            id=1, year=2025, company="Test", amount=Decimal("2400"),
            unit="l", vehicle="auto", fuel="benzyna",
            emission_tco2eq=Decimal("5.5"), raport="DEFRA 2024",
        )
        assert r.emission_tco2eq == Decimal("5.5")
        assert r.raport == "DEFRA 2024"

    def test_invalid_fuel(self):
        with pytest.raises(ValidationError, match="Nieznany typ paliwa"):
            MobileCombustion(
                id=1, year=2025, company="Test", amount=Decimal("100"),
                unit="l", vehicle="auto", fuel="kerozyna",
            )


class TestFugitiveEmissionModel:
    def test_valid_record(self):
        r = FugitiveEmission(
            id=1, year=2025, company="Test", amount=Decimal("5"),
            unit="kg", installation="klima", product="R410A",
        )
        assert r.product == "R410A"

    def test_emission_default_none(self):
        r = FugitiveEmission(
            id=1, year=2025, company="Test", amount=Decimal("5"),
            unit="kg", installation="klima", product="R410A",
        )
        assert r.emission_tco2eq is None


class TestProcessEmissionModel:
    def test_valid_record(self):
        r = ProcessEmission(
            id=1, year=2025, company="Test", amount=Decimal("100"),
            unit="t", process="kalcynacja", product="wapno",
        )
        assert r.process == "kalcynacja"


class TestEnergyConsumptionModel:
    def test_valid_record(self):
        r = EnergyConsumption(
            id=1, year=2025, company="Test", amount=Decimal("450"),
            unit="MWh", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        assert r.energy_type == "Energia elektryczna nie OZE"
        assert r.emission_tco2eq is None


class TestEmissionFactorModel:
    def test_valid_factor(self):
        f = EmissionFactor(
            id=1, factor_name="diesel", country="Polska",
            factor=Decimal("0.00268"), unit_factor="tCO2e/l", source="DEFRA",
        )
        assert f.factor == Decimal("0.00268")

    def test_negative_factor_rejected(self):
        with pytest.raises(ValidationError):
            EmissionFactor(
                id=1, factor_name="test", country="PL",
                factor=Decimal("-1"), unit_factor="t/t",
            )


class TestUnitConverterModel:
    def test_valid_converter(self):
        c = UnitConverter(
            id=1, unit_from="MWh", unit_to="kWh", factor=Decimal("1000"),
        )
        assert c.factor == Decimal("1000")

    def test_zero_factor_rejected(self):
        with pytest.raises(ValidationError):
            UnitConverter(
                id=1, unit_from="t", unit_to="kg", factor=Decimal("0"),
            )


class TestCompanyModel:
    def test_valid_company(self):
        c = Company(
            co_id=0, co_name="Test", co_country="PL", co_city="W-wa",
            co_street="ul. 1", co_zip="00-001", co_tel="+48 22 100 2000",
            co_mail="a@b.pl", co_krs="0000112233", co_regon="123456789",
            co_nip="5261234567", cg_name="Grupa",
        )
        assert c.co_name == "Test"

    def test_invalid_email(self):
        with pytest.raises(ValidationError, match="Nieprawidłowy email"):
            Company(
                co_id=0, co_name="Test", co_country="PL", co_city="W",
                co_street="u", co_zip="0", co_tel="+48 22 100",
                co_mail="nie-email", co_krs="0000112233",
                co_regon="123456789", co_nip="5261234567", cg_name="G",
            )

    def test_invalid_nip(self):
        with pytest.raises(ValidationError, match="NIP musi mieć 10 cyfr"):
            Company(
                co_id=0, co_name="Test", co_country="PL", co_city="W",
                co_street="u", co_zip="0", co_tel="+48 22 100",
                co_mail="a@b.pl", co_krs="0000112233",
                co_regon="123456789", co_nip="123", cg_name="G",
            )


class TestUserPermissionModel:
    def test_valid_admin(self):
        p = UserPermission(id=1, login="admin1", role="admin")
        assert p.role == "admin"

    def test_valid_user(self):
        p = UserPermission(id=2, login="user1", role="użytkownik")
        assert p.role == "użytkownik"

    def test_invalid_role(self):
        with pytest.raises(ValidationError, match="Nieznana rola"):
            UserPermission(id=3, login="x", role="superadmin")


class TestUserAuthorizationModel:
    def test_bool_parsing(self):
        a = UserAuthorization(
            id=1, login="test", company="Firma",
            save="TRUE", read="FALSE",
        )
        assert a.save is True
        assert a.read is False

    def test_bool_parsing_tak(self):
        a = UserAuthorization(
            id=1, login="test", company="Firma",
            save="TAK", read="NIE",
        )
        assert a.save is True
        assert a.read is False
