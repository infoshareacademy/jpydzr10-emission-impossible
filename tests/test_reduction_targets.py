"""Testy celów redukcji emisji i symulacji what-if."""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.application.class_models import ReductionTarget


class TestReductionTargetModel:
    """Testy walidacji modelu ReductionTarget."""

    def test_valid_target(self):
        """Poprawny cel redukcji."""
        t = ReductionTarget(
            id=1, company="TestFirma", target_name="SBTi 1.5C",
            base_year=2024, target_year=2030, reduction_pct=Decimal("42"),
            scope="1+2",
        )
        assert t.reduction_pct == Decimal("42")
        assert t.scope == "1+2"
        assert t.notes is None

    def test_target_year_must_be_after_base(self):
        """Rok docelowy musi być późniejszy niż bazowy."""
        with pytest.raises(ValidationError, match="musi być późniejszy"):
            ReductionTarget(
                id=1, company="Test", target_name="Test",
                base_year=2025, target_year=2025,
                reduction_pct=Decimal("10"), scope="1",
            )

    def test_invalid_scope(self):
        """Nieprawidłowy zakres powoduje błąd."""
        with pytest.raises(ValidationError, match="Nieprawidłowy zakres"):
            ReductionTarget(
                id=1, company="Test", target_name="Test",
                base_year=2024, target_year=2030,
                reduction_pct=Decimal("10"), scope="3",
            )

    def test_reduction_pct_range(self):
        """Cel redukcji musi być w zakresie 0-100%."""
        with pytest.raises(ValidationError):
            ReductionTarget(
                id=1, company="Test", target_name="Test",
                base_year=2024, target_year=2030,
                reduction_pct=Decimal("0"), scope="1+2",
            )
        with pytest.raises(ValidationError):
            ReductionTarget(
                id=1, company="Test", target_name="Test",
                base_year=2024, target_year=2030,
                reduction_pct=Decimal("101"), scope="1+2",
            )

    def test_scope_1_only(self):
        """Cel na Scope 1."""
        t = ReductionTarget(
            id=1, company="Test", target_name="Scope 1 only",
            base_year=2024, target_year=2030,
            reduction_pct=Decimal("30"), scope="1",
        )
        assert t.scope == "1"

    def test_scope_2_only(self):
        """Cel na Scope 2."""
        t = ReductionTarget(
            id=1, company="Test", target_name="Scope 2 only",
            base_year=2024, target_year=2030,
            reduction_pct=Decimal("50"), scope="2",
        )
        assert t.scope == "2"


class TestReductionTargetRepository:
    """Testy repozytorium celów redukcji."""

    def test_read_target_from_csv(self, repos):
        """Odczyt celu z CSV."""
        targets = repos.reduction_targets.get_for_company("TestFirma A")
        assert len(targets) == 1
        t = targets[0]
        assert t.target_name == "SBTi 1.5C"
        assert t.base_year == 2024
        assert t.target_year == 2030
        assert t.reduction_pct == Decimal("42")

    def test_no_targets_for_unknown_company(self, repos):
        """Brak celów dla nieznanej firmy."""
        targets = repos.reduction_targets.get_for_company("Nieznana")
        assert targets == []


class TestReductionPath:
    """Testy ścieżki redukcji liniowej."""

    def test_linear_path(self, uc):
        """Ścieżka liniowa: emisja bazowa 100, cel -42% w 6 lat."""
        target = ReductionTarget(
            id=1, company="Test", target_name="Test",
            base_year=2024, target_year=2030,
            reduction_pct=Decimal("42"), scope="1+2",
        )
        path = uc.get_reduction_path(target, Decimal("100"))

        assert len(path) == 7  # 2024, 2025, ..., 2030
        assert path[0]["year"] == 2024
        assert path[0]["target_emission"] == Decimal("100.000")
        assert path[-1]["year"] == 2030
        assert path[-1]["target_emission"] == Decimal("58.000")

    def test_path_never_negative(self, uc):
        """Ścieżka nie schodzi poniżej 0."""
        target = ReductionTarget(
            id=1, company="Test", target_name="Test",
            base_year=2024, target_year=2025,
            reduction_pct=Decimal("100"), scope="1",
        )
        path = uc.get_reduction_path(target, Decimal("50"))
        assert path[-1]["target_emission"] == Decimal("0")


class TestSimulationWhatIf:
    """Testy symulacji what-if."""

    def test_oze_switch_reduces_scope2(self, uc):
        """Przejście na OZE zmniejsza Scope 2."""
        result = uc.simulate_what_if("TestFirma A", 2025, [
            {"strategy": "oze_switch", "params": {"pct": 50}},
        ])
        baseline_s2 = result["baseline"]["scope2_energy"]
        sim_s2 = result["simulated"]["scope2_energy"]

        assert sim_s2 < baseline_s2
        assert sim_s2 == (baseline_s2 * Decimal("0.5")).quantize(Decimal("0.001"))

    def test_efficiency_reduces_all(self, uc):
        """Poprawa efektywności zmniejsza wszystkie scope."""
        result = uc.simulate_what_if("TestFirma A", 2025, [
            {"strategy": "efficiency", "params": {"pct": 20}},
        ])
        assert result["simulated"]["total"] < result["baseline"]["total"]
        assert result["savings"] > 0
        expected_pct = Decimal("20.0")
        assert abs(result["savings_pct"] - expected_pct) < Decimal("0.5")

    def test_custom_reduction(self, uc):
        """Własna redukcja procentowa."""
        result = uc.simulate_what_if("TestFirma A", 2025, [
            {"strategy": "custom", "params": {
                "scope1_reduction_pct": 30,
                "scope2_reduction_pct": 50,
            }},
        ])
        b = result["baseline"]
        s = result["simulated"]

        b_scope1 = b["scope1_stationary"] + b["scope1_mobile"] + b["scope1_fugitive"] + b["scope1_process"]
        s_scope1 = s["scope1_stationary"] + s["scope1_mobile"] + s["scope1_fugitive"] + s["scope1_process"]
        if b_scope1 > 0:
            assert abs(s_scope1 / b_scope1 - Decimal("0.7")) < Decimal("0.01")

        if b["scope2_energy"] > 0:
            assert abs(s["scope2_energy"] / b["scope2_energy"] - Decimal("0.5")) < Decimal("0.01")

    def test_combined_scenarios(self, uc):
        """Wiele scenariuszy łączy się kumulatywnie."""
        result = uc.simulate_what_if("TestFirma A", 2025, [
            {"strategy": "oze_switch", "params": {"pct": 100}},
            {"strategy": "efficiency", "params": {"pct": 10}},
        ])
        assert result["simulated"]["scope2_energy"] == Decimal("0")
        assert result["savings"] > 0

    def test_no_data_returns_zero_savings(self, uc):
        """Symulacja bez danych → brak oszczędności."""
        result = uc.simulate_what_if("TestFirma A", 2020, [
            {"strategy": "efficiency", "params": {"pct": 50}},
        ])
        assert result["savings"] == Decimal("0")
        assert result["savings_pct"] == Decimal("0")
