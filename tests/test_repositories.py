"""
Testy repozytoriów — CRUD, wyszukiwanie wskaźników, uprawnienia.
"""

import pytest
from decimal import Decimal


class TestFactorRepository:
    """Testy FactorRepository.get_factor — wyszukiwanie wskaźników emisji."""

    def test_find_by_exact_name(self, repos):
        f = repos.factors.get_factor("diesel", "Polska")
        assert f is not None
        assert f.factor == Decimal("0.00268")

    def test_find_by_partial_name(self, repos):
        """Wyszukiwanie po fragmencie nazwy (substring match)."""
        f = repos.factors.get_factor("gaz", "Polska")
        assert f is not None
        assert "gaz" in f.factor_name.lower()

    def test_find_with_country_filter(self, repos):
        f = repos.factors.get_factor("diesel", "Polska")
        assert f is not None
        assert f.country == "Polska"

    def test_not_found_returns_none(self, repos):
        f = repos.factors.get_factor("nieistniejący_wskaźnik", "Polska")
        assert f is None

    def test_case_insensitive(self, repos):
        f = repos.factors.get_factor("DIESEL", "Polska")
        assert f is not None

    def test_unit_factor_format(self, repos):
        """Wskaźnik paliwa ma format tCO2e/jednostka."""
        f = repos.factors.get_factor("diesel", "Polska")
        assert "/" in f.unit_factor
        assert "CO2" in f.unit_factor


class TestConverterRepository:
    """Testy ConverterRepository — konwersje dwukierunkowe."""

    def test_forward_conversion(self, repos):
        result = repos.converters.convert(Decimal("1"), "MWh", "kWh")
        assert result == Decimal("1000")

    def test_reverse_conversion(self, repos):
        """Odwrotna konwersja — dzielenie przez factor."""
        result = repos.converters.convert(Decimal("1000"), "kWh", "MWh")
        assert result == Decimal("1")

    def test_missing_conversion_raises(self, repos):
        with pytest.raises(ValueError):
            repos.converters.convert(Decimal("1"), "l", "GJ")


class TestCompanyRepository:
    """Testy CompanyRepository — wyszukiwanie firm."""

    def test_get_by_name(self, repos):
        c = repos.companies.get_by_name("TestFirma A")
        assert c is not None
        assert c.co_name == "TestFirma A"

    def test_get_by_name_case_insensitive(self, repos):
        c = repos.companies.get_by_name("testfirma a")
        assert c is not None

    def test_get_by_name_not_found(self, repos):
        c = repos.companies.get_by_name("NieIstniejąca")
        assert c is None

    def test_get_groups(self, repos):
        groups = repos.companies.get_groups()
        assert "TestGrupa" in groups

    def test_get_by_group(self, repos):
        companies = repos.companies.get_by_group("TestGrupa")
        assert len(companies) == 2


class TestAuthorisationRepository:
    """Testy AuthorisationRepository — uprawnienia użytkowników."""

    def test_read_companies(self, repos):
        companies = repos.authorisations.get_companies_for_user("tester", read_only=True)
        assert "TestFirma A" in companies
        assert "TestFirma B" in companies

    def test_save_companies(self, repos):
        """Uprawnienia do zapisu — mniejsza lista niż do odczytu."""
        companies = repos.authorisations.get_companies_for_user("tester", read_only=False)
        assert "TestFirma A" in companies
        assert "TestFirma B" not in companies  # save=FALSE

    def test_unknown_user_empty(self, repos):
        companies = repos.authorisations.get_companies_for_user("nieznany")
        assert companies == []


class TestPermissionRepository:
    """Testy PermissionRepository — role użytkowników."""

    def test_admin_role(self, repos):
        assert repos.permissions.is_admin("admin1") is True
        assert repos.permissions.get_role("admin1") == "admin"

    def test_user_role(self, repos):
        assert repos.permissions.is_admin("tester") is False
        assert repos.permissions.get_role("tester") == "użytkownik"

    def test_unknown_user_default(self, repos):
        """Nieznany użytkownik → domyślna rola 'użytkownik'."""
        assert repos.permissions.get_role("nieznany") == "użytkownik"
        assert repos.permissions.is_admin("nieznany") is False


class TestCsvRepositoryCRUD:
    """Testy podstawowych operacji CRUD na CsvRepository."""

    def test_get_all_returns_records(self, repos):
        records, errors = repos.stationary.get_all()
        assert len(records) > 0
        assert len(errors) == 0

    def test_get_by_id(self, repos):
        r = repos.stationary.get_by_id(1)
        assert r is not None
        assert r.id == 1

    def test_get_by_id_not_found(self, repos):
        r = repos.stationary.get_by_id(9999)
        assert r is None

    def test_get_filtered(self, repos):
        records = repos.stationary.get_filtered(company="TestFirma A")
        assert all(r.company == "TestFirma A" for r in records)

    def test_next_id(self, repos):
        nid = repos.stationary.next_id()
        records, _ = repos.stationary.get_all()
        max_id = max(r.id for r in records)
        assert nid == max_id + 1
