"""
Testy walidacji spójności danych między tabelami.
Sprawdza czy firmy w tabelach emisyjnych istnieją w tbl_companies
oraz czy niespójność emission_tco2eq/raport jest wykrywana.
"""

import pytest
from decimal import Decimal


class TestDataConsistency:
    """Testy validate_data_consistency."""

    def test_detects_missing_company_in_authorisations(self, uc):
        """Wykrywa firmę w autoryzacjach, która nie istnieje w tbl_companies."""
        issues = uc.validate_data_consistency()
        missing = [i for i in issues if "NieistniejącaFirma" in i]
        assert len(missing) >= 1

    def test_valid_companies_not_flagged(self, uc):
        """TestFirma A i B istnieją — nie powinny być zgłoszone."""
        issues = uc.validate_data_consistency()
        false_positives = [i for i in issues if "TestFirma A" in i and "nie istnieje" in i]
        assert len(false_positives) == 0

    def test_detects_raport_without_emission(self, uc):
        """Wykrywa raport podany ale emission_tco2eq puste."""
        issues = uc.validate_data_consistency()
        raport_issues = [i for i in issues if "raport=" in i and "emission_tco2eq puste" in i]
        # ID 3: raport='KOBiZE', emission_tco2eq puste
        assert len(raport_issues) >= 1

    def test_consistent_record_not_flagged(self, uc):
        """emission_tco2eq + raport oba podane → nie powinien być zgłoszony."""
        issues = uc.validate_data_consistency()
        # ID 1: emission_tco2eq=99.999 + raport='KOBiZE' — poprawny rekord
        flagged = [i for i in issues if "ID 1" in i and "spalanie stacjonarne" in i]
        assert len(flagged) == 0


class TestFactorVerification:
    """Testy verify_factors_and_converters — brakujące wskaźniki."""

    def test_all_factors_present(self, uc):
        """Dla testowych danych — wszystkie wskaźniki powinny istnieć."""
        issues = uc.verify_factors_and_converters("Polska")
        # Nie powinno być braków wskaźników (bo testowe dane mają dopasowane factors)
        factor_issues = [i for i in issues if "Brak wskaźnika" in i["info"]]
        assert len(factor_issues) == 0


class TestAvailableYears:
    """Testy get_available_years."""

    def test_returns_sorted_years(self, uc):
        years = uc.get_available_years("TestFirma A")
        assert years == sorted(years)
        assert 2024 in years
        assert 2025 in years

    def test_empty_for_unknown_company(self, uc):
        years = uc.get_available_years("NieistniejącaFirma")
        assert years == []
