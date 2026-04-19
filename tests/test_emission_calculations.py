"""
Testy obliczania emisji — _calculate_emission_for_record()
Weryfikują poprawność obliczeń dla wszystkich kategorii Scope 1 i Scope 2.
Każdy test sprawdza: ilość × (konwersja jednostek) × wskaźnik = tCO2e

Uwaga: wskaźniki są teraz wersjonowane per rok (pole year w tbl_factors.csv).
Testy przekazują year=2024 wprost — odpowiada wskaźnikom z conftest.
Bez podania roku — get_factor() zwraca najnowszy dostępny wskaźnik.
"""

import pytest
from decimal import Decimal, ROUND_HALF_UP


def R(d: Decimal) -> Decimal:
    """Zaokrągla do 3 miejsc po przecinku (jak w generate_summary)."""
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


class TestStationaryCombustion:
    """Obliczenia emisji ze spalania stacjonarnego (Scope 1)."""

    def test_gaz_ziemny_m3(self, uc):
        """Gaz ziemny: 10000 m3 × 0.00202 tCO2e/m3 = 20.200 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("10000"), "m3", "gaz ziemny", year=2024)
        assert R(result) == Decimal("20.200")

    def test_gaz_ziemny_5000_m3(self, uc):
        """Gaz ziemny: 5000 m3 × 0.00202 = 10.100 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("5000"), "m3", "gaz ziemny", year=2024)
        assert R(result) == Decimal("10.100")

    def test_wegiel_kamienny_200t(self, uc):
        """Węgiel kamienny: 200 t × 2.446 = 489.200 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("200"), "t", "węgiel kamienny", year=2024)
        assert R(result) == Decimal("489.200")

    def test_wegiel_kamienny_1kg(self, uc):
        """Węgiel kamienny: 1 kg → 0.001 t × 2.446 = 0.002446 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("1"), "kg", "węgiel kamienny", year=2024)
        # 1 kg = 0.001 t; 0.001 × 2.446 = 0.002446
        assert R(result) == Decimal("0.002")

    def test_olej_opalowy_lekki_15t(self, uc):
        """Olej opałowy lekki: 15 t × 3.17 = 47.550 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("15"), "t", "olej opałowy lekki", year=2024)
        assert R(result) == Decimal("47.550")

    def test_biomasa_zero_emission(self, uc):
        """Biomasa: wskaźnik = 0 → emisja = 0 (neutralna CO2)."""
        result = uc._calculate_emission_for_record(
            Decimal("1000"), "t", "biomasa", year=2024)
        assert result == Decimal("0")

    def test_brak_wskaznika(self, uc):
        """Nieistniejące paliwo → emisja = 0."""
        result = uc._calculate_emission_for_record(
            Decimal("100"), "t", "nieistniejące_paliwo", year=2024)
        assert result == Decimal("0")


class TestMobileCombustion:
    """Obliczenia emisji ze spalania mobilnego (Scope 1)."""

    def test_benzyna_2400l(self, uc):
        """Benzyna: 2400 l × 0.00232 = 5.568 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("2400"), "l", "benzyna", year=2024)
        assert R(result) == Decimal("5.568")

    def test_diesel_5000l(self, uc):
        """Diesel rok 2024: 5000 l × 0.00268 = 13.400 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("5000"), "l", "diesel", year=2024)
        assert R(result) == Decimal("13.400")

    def test_diesel_5000l_year_2025(self, uc):
        """Diesel rok 2025: 5000 l × 0.00270 = 13.500 tCO2e (wskaźnik 2025 z conftest)"""
        result = uc._calculate_emission_for_record(
            Decimal("5000"), "l", "diesel", year=2025)
        # conftest ma diesel 2025 = 0.00270
        assert R(result) == Decimal("13.500")

    def test_lpg_1000l(self, uc):
        """LPG: 1000 l × 0.00163 = 1.630 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("1000"), "l", "LPG", year=2024)
        assert R(result) == Decimal("1.630")

    def test_diesel_zero_litres(self, uc):
        """0 litrów diesel → 0 emisji."""
        result = uc._calculate_emission_for_record(
            Decimal("0"), "l", "diesel", year=2024)
        assert result == Decimal("0")

    def test_diesel_large_fleet(self, uc):
        """Diesel: 92000 l × 0.00268 = 246.560 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("92000"), "l", "diesel", year=2024)
        assert R(result) == Decimal("246.560")

    def test_fallback_to_latest_year(self, uc):
        """Brak wskaźnika dla roku 2023 → fallback na najnowszy (2025 w conftest)."""
        result = uc._calculate_emission_for_record(
            Decimal("5000"), "l", "diesel", year=2023)
        # fallback na rok 2025 → 5000 × 0.00270 = 13.500
        assert R(result) == Decimal("13.500")


class TestFugitiveEmission:
    """Obliczenia emisji niezorganizowanych — czynniki chłodnicze (Scope 1).
    Wskaźniki w kgCO2e/kg → wynik konwertowany na tCO2e."""

    def test_r410a_5kg(self, uc):
        """R410A: 5 kg × 2088 kgCO2e/kg = 10440 kgCO2e = 10.440 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("5"), "kg", "R410A", year=2024)
        assert R(result) == Decimal("10.440")

    def test_r32_2kg(self, uc):
        """R32: 2 kg × 675 kgCO2e/kg = 1350 kgCO2e = 1.350 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("2"), "kg", "R32", year=2024)
        assert R(result) == Decimal("1.350")

    def test_r410a_large_leak(self, uc):
        """R410A: 50 kg × 2088 = 104400 kgCO2e = 104.400 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("50"), "kg", "R410A", year=2024)
        assert R(result) == Decimal("104.400")


class TestProcessEmission:
    """Obliczenia emisji procesowych (Scope 1)."""

    def test_kalcynacja_100t(self, uc):
        """Kalcynacja: 100 t × 0.780 = 78.000 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("100"), "t", "kalcynacja", year=2024)
        assert R(result) == Decimal("78.000")

    def test_kalcynacja_small(self, uc):
        """Kalcynacja: 1 t × 0.780 = 0.780 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("1"), "t", "kalcynacja", year=2024)
        assert R(result) == Decimal("0.780")


class TestScope2Energy:
    """Obliczenia emisji Scope 2 — zużycie energii."""

    def test_elektr_nie_oze_450mwh(self, uc):
        """Energia elektryczna nie OZE: 450 MWh × 0.709 = 319.050 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("450"), "MWh", "Energia elektryczna nie OZE", year=2024)
        assert R(result) == Decimal("319.050")

    def test_elektr_oze_zerowa(self, uc):
        """Energia elektryczna z OZE → emisja = 0."""
        result = uc._calculate_emission_for_record(
            Decimal("100"), "MWh", "Energia elektryczna z OZE", year=2024)
        assert result == Decimal("0")  # albo Decimal("0.000")

    def test_cieplo_280gj(self, uc):
        """Energia cieplna: 280 GJ × 0.292 = 81.760 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("280"), "GJ", "Energia cieplna", year=2024)
        assert R(result) == Decimal("81.760")

    def test_chlod_340gj(self, uc):
        """Chłód: 340 GJ × 0.180 = 61.200 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("340"), "GJ", "Chłód", year=2024)
        assert R(result) == Decimal("61.200")

    def test_elektr_kwh_to_mwh_conversion(self, uc):
        """Energia elektryczna: 1000 kWh = 1 MWh × 0.709 = 0.709 tCO2e
        Wymaga konwersji kWh → MWh."""
        result = uc._calculate_emission_for_record(
            Decimal("1000"), "kWh", "Energia elektryczna nie OZE", year=2024)
        assert R(result) == Decimal("0.709")

    def test_cieplo_mj_conversion(self, uc):
        """Energia cieplna: 1000 MJ = 1 GJ × 0.292 = 0.292 tCO2e
        Wymaga konwersji MJ → GJ."""
        result = uc._calculate_emission_for_record(
            Decimal("1000"), "MJ", "Energia cieplna", year=2024)
        assert R(result) == Decimal("0.292")

    def test_large_industrial_electricity(self, uc):
        """Duże zużycie: 4800 MWh × 0.709 = 3403.200 tCO2e"""
        result = uc._calculate_emission_for_record(
            Decimal("4800"), "MWh", "Energia elektryczna nie OZE", year=2024)
        assert R(result) == Decimal("3403.200")

    def test_no_year_uses_latest(self, uc):
        """Bez year → get_factor zwraca najnowszy wskaźnik."""
        result_no_year = uc._calculate_emission_for_record(
            Decimal("5000"), "l", "diesel")
        result_latest = uc._calculate_emission_for_record(
            Decimal("5000"), "l", "diesel", year=2025)
        # oba powinny dać ten sam wynik (najnowszy = 2025)
        assert result_no_year == result_latest
