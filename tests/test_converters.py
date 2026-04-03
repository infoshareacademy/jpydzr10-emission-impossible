"""
Testy konwersji jednostek — ConverterRepository.convert()
Weryfikują poprawność przeliczania między jednostkami energii, masy i objętości.
"""

import pytest
from decimal import Decimal


class TestConverterBasic:
    """Podstawowe konwersje — te same jednostki, prosta konwersja wprost."""

    def test_same_unit_returns_unchanged(self, repos):
        """Ta sama jednostka → zwraca tę samą wartość bez konwersji."""
        result = repos.converters.convert(Decimal("100"), "MWh", "MWh")
        assert result == Decimal("100")

    def test_same_unit_kg(self, repos):
        result = repos.converters.convert(Decimal("55.5"), "kg", "kg")
        assert result == Decimal("55.5")


class TestConverterEnergy:
    """Konwersje jednostek energii: MWh, kWh, GJ, MJ."""

    def test_mwh_to_kwh(self, repos):
        # 1 MWh = 1000 kWh
        result = repos.converters.convert(Decimal("1"), "MWh", "kWh")
        assert result == Decimal("1000")

    def test_kwh_to_mwh(self, repos):
        # 1000 kWh = 1 MWh (odwrotność)
        result = repos.converters.convert(Decimal("1000"), "kWh", "MWh")
        assert result == Decimal("1")

    def test_mwh_to_gj(self, repos):
        # 1 MWh = 3.6 GJ
        result = repos.converters.convert(Decimal("1"), "MWh", "GJ")
        assert result == Decimal("3.6")

    def test_gj_to_mwh(self, repos):
        # 3.6 GJ = 1 MWh
        result = repos.converters.convert(Decimal("3.6"), "GJ", "MWh")
        assert result == Decimal("1")

    def test_mwh_to_mj(self, repos):
        # 1 MWh = 3600 MJ
        result = repos.converters.convert(Decimal("1"), "MWh", "MJ")
        assert result == Decimal("3600")

    def test_gj_to_mj(self, repos):
        # 1 GJ = 1000 MJ
        result = repos.converters.convert(Decimal("1"), "GJ", "MJ")
        assert result == Decimal("1000")

    def test_kwh_to_mj(self, repos):
        # 1 kWh = 3.6 MJ
        result = repos.converters.convert(Decimal("1"), "kWh", "MJ")
        assert result == Decimal("3.6")

    def test_large_energy_conversion(self, repos):
        # 450 MWh → kWh = 450000
        result = repos.converters.convert(Decimal("450"), "MWh", "kWh")
        assert result == Decimal("450000")

    def test_gj_to_kwh(self, repos):
        # 1 GJ = 277.778 kWh
        result = repos.converters.convert(Decimal("1"), "GJ", "kWh")
        assert result == Decimal("277.778")


class TestConverterMass:
    """Konwersje jednostek masy: t, kg, Mg, g."""

    def test_t_to_kg(self, repos):
        # 1 t = 1000 kg
        result = repos.converters.convert(Decimal("1"), "t", "kg")
        assert result == Decimal("1000")

    def test_kg_to_t(self, repos):
        # 1000 kg = 1 t
        result = repos.converters.convert(Decimal("1000"), "kg", "t")
        assert result == Decimal("1")

    def test_mg_to_t(self, repos):
        # 1 Mg = 1 t
        result = repos.converters.convert(Decimal("1"), "Mg", "t")
        assert result == Decimal("1")

    def test_mg_to_kg(self, repos):
        # 1 Mg = 1000 kg
        result = repos.converters.convert(Decimal("1"), "Mg", "kg")
        assert result == Decimal("1000")

    def test_t_to_g(self, repos):
        # 1 t = 1000000 g
        result = repos.converters.convert(Decimal("1"), "t", "g")
        assert result == Decimal("1000000")

    def test_small_mass_conversion(self, repos):
        # 0.5 kg → t = 0.0005
        result = repos.converters.convert(Decimal("0.5"), "kg", "t")
        assert result == Decimal("0.0005")

    def test_large_mass_conversion(self, repos):
        # 15 t → kg = 15000
        result = repos.converters.convert(Decimal("15"), "t", "kg")
        assert result == Decimal("15000")


class TestConverterVolume:
    """Konwersje objętości: m3, l."""

    def test_m3_to_l(self, repos):
        # 1 m3 = 1000 l
        result = repos.converters.convert(Decimal("1"), "m3", "l")
        assert result == Decimal("1000")

    def test_l_to_m3(self, repos):
        # 1000 l = 1 m3
        result = repos.converters.convert(Decimal("1000"), "l", "m3")
        assert result == Decimal("1")

    def test_large_volume(self, repos):
        # 12000 m3 → l = 12000000
        result = repos.converters.convert(Decimal("12000"), "m3", "l")
        assert result == Decimal("12000000")


class TestConverterErrors:
    """Testy obsługi błędów konwersji."""

    def test_unknown_conversion_raises(self, repos):
        """Brak przelicznika → ValueError."""
        with pytest.raises(ValueError, match="Brak przelicznika"):
            repos.converters.convert(Decimal("1"), "m3", "MWh")

    def test_incompatible_units(self, repos):
        """Konwersja między niekompatybilnymi jednostkami → ValueError."""
        with pytest.raises(ValueError):
            repos.converters.convert(Decimal("1"), "l", "kg")

    def test_zero_amount(self, repos):
        """Konwersja zera → zawsze zero."""
        result = repos.converters.convert(Decimal("0"), "MWh", "GJ")
        assert result == Decimal("0")
