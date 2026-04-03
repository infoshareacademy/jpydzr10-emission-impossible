"""
Testy generate_summary — podsumowanie emisji w pamięci.
Sprawdza poprawność logiki:
- raport=TRUE → bierze emission z CSV
- raport=FALSE → oblicza z ilości × wskaźnik
- Scope 2 → zawsze oblicza z wskaźnika
- Trendy rok do roku
"""

import pytest
from decimal import Decimal, ROUND_HALF_UP


def R(d: Decimal) -> Decimal:
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


class TestGenerateSummary:
    """Testy generate_summary — główna metoda raportowania."""

    def test_stationary_raport_true_uses_csv_value(self, uc):
        """raport=TRUE z podaną emisją → używa wartości z CSV (99.999)."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        # ID 1: raport=TRUE, emission=99.999
        # ID 2: raport=FALSE, 5000 m3 × 0.00202 = 10.100
        expected_stationary = Decimal("99.999") + Decimal("10.100")
        assert s["scope1_stationary"] == R(expected_stationary)

    def test_stationary_raport_false_calculates(self, uc):
        """raport=FALSE → oblicza emisję z amount × wskaźnik."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        # Sprawdź że stationary nie jest 0 (bo raport=FALSE oblicza)
        assert s["scope1_stationary"] > 0

    def test_stationary_raport_true_emission_zero_calculates(self, uc):
        """raport=TRUE ale emission=0 → oblicza z wskaźnika (bo emission nie >0)."""
        s = uc.generate_summary(2025, 2025, "TestFirma B")
        # ID 3: raport=TRUE, emission=0, 200 t × 2.446 = 489.200
        # generate_summary: if r.raport and r.emission > 0 → bierze z CSV
        # tu emission=0 więc warunek nie spełniony → oblicza
        assert s["scope1_stationary"] == Decimal("489.200")

    def test_mobile_always_calculates(self, uc):
        """Spalanie mobilne — zawsze oblicza z wskaźnika, ignoruje CSV emission."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        # ID 1: 2400 l benzyna × 0.00232 = 5.568
        # ID 2: 5000 l diesel × 0.00268 = 13.400
        expected = Decimal("5.568") + Decimal("13.400")
        assert s["scope1_mobile"] == R(expected)

    def test_mobile_lpg(self, uc):
        """LPG w spalaniu mobilnym: 1000 l × 0.00163 = 1.630."""
        s = uc.generate_summary(2025, 2025, "TestFirma B")
        assert s["scope1_mobile"] == Decimal("1.630")

    def test_fugitive_r410a(self, uc):
        """Emisje niezorganizowane R410A: 5 kg × 2088 kgCO2e/kg → 10.440 tCO2e."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        assert s["scope1_fugitive"] == Decimal("10.440")

    def test_fugitive_r32(self, uc):
        """Emisje niezorganizowane R32: 2 kg × 675 → 1.350 tCO2e."""
        s = uc.generate_summary(2025, 2025, "TestFirma B")
        assert s["scope1_fugitive"] == Decimal("1.350")

    def test_process_kalcynacja(self, uc):
        """Emisje procesowe — kalcynacja: 100 t × 0.780 = 78.000."""
        s = uc.generate_summary(2025, 2025, "TestFirma B")
        assert s["scope1_process"] == Decimal("78.000")

    def test_scope2_energy_non_oze(self, uc):
        """Scope 2: oblicza z wskaźnika (nie z CSV)."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        # ID 1: 450 MWh × 0.709 = 319.050
        # ID 2: 280 GJ × 0.292 = 81.760
        # ID 3: 100 MWh OZE × 0 = 0
        expected = Decimal("319.050") + Decimal("81.760") + Decimal("0")
        assert s["scope2_energy"] == R(expected)

    def test_scope2_oze_zero(self, uc):
        """OZE nie dodaje emisji do sumy Scope 2."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        # Gdyby OZE miało niezerowy wskaźnik, scope2 byłoby większe
        assert s["scope2_energy"] == Decimal("400.810")

    def test_total_is_sum_of_scopes(self, uc):
        """Total = suma wszystkich scope1_* + scope2_*."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        calculated_total = (
            s["scope1_stationary"] + s["scope1_mobile"]
            + s["scope1_fugitive"] + s["scope1_process"]
            + s["scope2_energy"]
        )
        assert s["total"] == R(calculated_total)

    def test_empty_company_returns_zeros(self, uc):
        """Firma bez danych → wszystkie wartości = 0."""
        s = uc.generate_summary(2025, 2025, "NieistniejącaFirma")
        assert s["total"] == Decimal("0")
        assert s["scope1_stationary"] == Decimal("0")
        assert s["scope1_mobile"] == Decimal("0")

    def test_year_range_filtering(self, uc):
        """Tylko dane z podanego zakresu lat."""
        s_2025 = uc.generate_summary(2025, 2025, "TestFirma A")
        s_2024 = uc.generate_summary(2024, 2024, "TestFirma A")
        s_all = uc.generate_summary(2024, 2025, "TestFirma A")
        # Suma za oba lata powinna być większa niż za jeden
        assert s_all["total"] > s_2025["total"]
        assert s_all["total"] > s_2024["total"]

    def test_csv_emission_not_used_for_mobile(self, uc):
        """Spalanie mobilne: CSV emission=0, ale summary oblicza > 0."""
        s = uc.generate_summary(2025, 2025, "TestFirma A")
        assert s["scope1_mobile"] > 0


class TestTrendReport:
    """Testy raportu trendów rok do roku."""

    def test_trend_returns_data_per_year(self, uc):
        """Trend za 2024-2025 → 2 wpisy."""
        trends = uc.generate_trend_report("TestFirma A", 2024, 2025)
        assert len(trends) == 2
        assert trends[0]["year"] == 2024
        assert trends[1]["year"] == 2025

    def test_trend_first_year_no_change(self, uc):
        """Pierwszy rok nie ma % zmiany."""
        trends = uc.generate_trend_report("TestFirma A", 2024, 2025)
        assert trends[0]["change_pct"] is None

    def test_trend_second_year_has_change(self, uc):
        """Drugi rok ma obliczoną % zmianę."""
        trends = uc.generate_trend_report("TestFirma A", 2024, 2025)
        assert trends[1]["change_pct"] is not None

    def test_trend_total_matches_summary(self, uc):
        """Total w trendzie = total w generate_summary dla tego samego roku."""
        trends = uc.generate_trend_report("TestFirma A", 2025, 2025)
        summary = uc.generate_summary(2025, 2025, "TestFirma A")
        assert trends[0]["total"] == summary["total"]

    def test_trend_scope1_total_correct(self, uc):
        """scope1_total = suma 4 kategorii Scope 1."""
        trends = uc.generate_trend_report("TestFirma A", 2025, 2025)
        t = trends[0]
        expected = (t["scope1_stationary"] + t["scope1_mobile"]
                    + t["scope1_fugitive"] + t["scope1_process"])
        assert t["scope1_total"] == expected
