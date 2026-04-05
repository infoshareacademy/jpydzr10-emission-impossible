"""Testy poziomów pewności danych (data_quality)."""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.application.class_models import (
    StationaryCombustion, MobileCombustion, EnergyConsumption,
    DATA_QUALITY_LEVELS,
)


class TestDataQualityValidation:
    """Testy walidacji pola data_quality w modelach Pydantic."""

    def test_valid_measured(self):
        """Wartość 'measured' jest akceptowana."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test", data_quality="measured",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality == "measured"

    def test_valid_calculated(self):
        """Wartość 'calculated' jest akceptowana."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test", data_quality="calculated",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality == "calculated"

    def test_valid_estimated(self):
        """Wartość 'estimated' jest akceptowana."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test", data_quality="estimated",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality == "estimated"

    def test_none_when_empty_string(self):
        """Pusty string → None (opcjonalne pole)."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test", data_quality="",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality is None

    def test_none_when_not_provided(self):
        """Pole pominięte → None (domyślna wartość)."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality is None

    def test_case_insensitive(self):
        """Walidator normalizuje do lowercase."""
        r = StationaryCombustion(
            id=1, year=2025, company="Test", data_quality="MEASURED",
            amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
            installation="piec",
        )
        assert r.data_quality == "measured"

    def test_invalid_value_raises(self):
        """Nieznana wartość powoduje błąd walidacji."""
        with pytest.raises(ValidationError, match="Nieznany poziom"):
            StationaryCombustion(
                id=1, year=2025, company="Test", data_quality="guessed",
                amount=Decimal("100"), unit="m3", fuel="gaz ziemny",
                installation="piec",
            )

    def test_data_quality_on_mobile(self):
        """Pole data_quality działa na MobileCombustion (dziedziczenie z BaseRecord)."""
        r = MobileCombustion(
            id=1, year=2025, company="Test", data_quality="estimated",
            amount=Decimal("50"), unit="l", vehicle="samochód",
            fuel="diesel",
        )
        assert r.data_quality == "estimated"

    def test_data_quality_on_energy(self):
        """Pole data_quality działa na EnergyConsumption."""
        r = EnergyConsumption(
            id=1, year=2025, company="Test", data_quality="measured",
            amount=Decimal("100"), unit="MWh", source="faktura",
            energy_source="Zakupiona", energy_type="Energia elektryczna nie OZE",
        )
        assert r.data_quality == "measured"


class TestDataQualityInRepository:
    """Testy odczytu data_quality z plików CSV przez repozytorium."""

    def test_read_data_quality_from_csv(self, repos):
        """Repozytorium poprawnie odczytuje data_quality z CSV."""
        records, errors = repos.stationary.get_all()
        # Rekord id=1 ma data_quality="measured" (z conftest)
        r1 = next(r for r in records if r.id == 1)
        assert r1.data_quality == "measured"

        # Rekord id=2 ma data_quality="calculated"
        r2 = next(r for r in records if r.id == 2)
        assert r2.data_quality == "calculated"

        # Rekord id=3 ma data_quality="estimated"
        r3 = next(r for r in records if r.id == 3)
        assert r3.data_quality == "estimated"

    def test_empty_data_quality_is_none(self, repos):
        """Puste data_quality w CSV → None."""
        records, _ = repos.mobile.get_all()
        # Rekord id=3 ma data_quality="" (z conftest)
        r3 = next(r for r in records if r.id == 3)
        assert r3.data_quality is None

    def test_data_quality_constants(self):
        """Stała DATA_QUALITY_LEVELS zawiera 3 dozwolone wartości."""
        assert DATA_QUALITY_LEVELS == {"measured", "calculated", "estimated"}
