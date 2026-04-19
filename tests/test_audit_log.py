"""
Testy rejestru zmian (audit log) — mechanizm triggerów.

Sprawdza:
- Poprawność modelu ChangeLog (walidacja, parsowanie datetime)
- Niezmienność logu (blokada update/delete)
- Automatyczne logowanie operacji INSERT/UPDATE/DELETE
- Poprawność pól previous_data / actual_data (JSON)
- Filtrowanie historii zmian (po tabeli, rekordzie, użytkowniku)
- Brak logowania gdy audit context nie jest ustawiony
"""

import json
import pytest
from datetime import datetime
from decimal import Decimal

from app.application.class_models import (
    ChangeLog, EnergyConsumption, StationaryCombustion,
)


# === Testy modelu ChangeLog ===

class TestChangeLogModel:
    """Testy walidacji modelu Pydantic ChangeLog."""

    def test_valid_insert(self):
        """Poprawny rekord INSERT — actual_data wypełnione, previous_data puste."""
        log = ChangeLog(
            id_rejestr_zmian=1,
            login="tester",
            date_change=datetime(2025, 6, 15, 14, 30, 0),
            table_name="tbl_e_cons",
            record_id="42",
            change_type="INSERT",
            previous_data=None,
            actual_data='{"id": 42, "amount": "100"}',
        )
        assert log.change_type == "INSERT"
        assert log.previous_data is None
        assert log.actual_data is not None

    def test_valid_update(self):
        """Poprawny rekord UPDATE — oba pola JSON wypełnione."""
        log = ChangeLog(
            id_rejestr_zmian=2,
            login="tester",
            date_change=datetime(2025, 6, 15, 14, 31, 0),
            table_name="tbl_companies",
            record_id="1",
            change_type="UPDATE",
            previous_data='{"co_city": "Warszawa"}',
            actual_data='{"co_city": "Kraków"}',
        )
        assert log.change_type == "UPDATE"
        assert log.previous_data is not None
        assert log.actual_data is not None

    def test_valid_delete(self):
        """Poprawny rekord DELETE — previous_data wypełnione, actual_data puste."""
        log = ChangeLog(
            id_rejestr_zmian=3,
            login="tester",
            date_change=datetime(2025, 6, 15, 14, 32, 0),
            table_name="tbl_e_cons",
            record_id="42",
            change_type="DELETE",
            previous_data='{"id": 42}',
            actual_data=None,
        )
        assert log.change_type == "DELETE"
        assert log.previous_data is not None
        assert log.actual_data is None

    def test_invalid_change_type(self):
        """Nieznany typ zmiany → ValidationError."""
        with pytest.raises(Exception):
            ChangeLog(
                id_rejestr_zmian=1,
                login="tester",
                date_change=datetime.now(),
                table_name="tbl_e_cons",
                record_id="1",
                change_type="TRUNCATE",
            )

    def test_change_type_case_insensitive(self):
        """Typ zmiany powinien być normalizowany do uppercase."""
        log = ChangeLog(
            id_rejestr_zmian=1,
            login="tester",
            date_change=datetime.now(),
            table_name="tbl_e_cons",
            record_id="1",
            change_type="insert",
        )
        assert log.change_type == "INSERT"

    def test_parse_datetime_from_string(self):
        """Parsowanie datetime z formatu string (jak w CSV)."""
        log = ChangeLog(
            id_rejestr_zmian=1,
            login="tester",
            date_change="2025-06-15 14:30:00",
            table_name="tbl_e_cons",
            record_id="1",
            change_type="INSERT",
        )
        assert log.date_change == datetime(2025, 6, 15, 14, 30, 0)

    def test_parse_datetime_iso_format(self):
        """Parsowanie datetime z formatu ISO."""
        log = ChangeLog(
            id_rejestr_zmian=1,
            login="tester",
            date_change="2025-06-15T14:30:00",
            table_name="tbl_e_cons",
            record_id="1",
            change_type="INSERT",
        )
        assert log.date_change.year == 2025

    def test_id_must_be_positive(self):
        """ID rejestru zmian musi być >= 1."""
        with pytest.raises(Exception):
            ChangeLog(
                id_rejestr_zmian=0,
                login="tester",
                date_change=datetime.now(),
                table_name="tbl_e_cons",
                record_id="1",
                change_type="INSERT",
            )


# === Testy ChangeLogRepository — niezmienność ===

class TestChangeLogRepositoryImmutability:
    """Audit log jest niezmienny — update i delete muszą być zablokowane."""

    def test_update_blocked(self, repos):
        """Update na rejestrze zmian powinien zwrócić błąd."""
        ok, msg = repos.change_log.update(1, {"login": "hacker"})
        assert ok is False
        assert "nie pozwala" in msg.lower() or "edycj" in msg.lower()

    def test_delete_blocked(self, repos):
        """Delete na rejestrze zmian powinien zwrócić błąd."""
        ok, msg = repos.change_log.delete(1)
        assert ok is False
        assert "nie pozwala" in msg.lower() or "usuwan" in msg.lower()


# === Testy automatycznego logowania (trigger) ===

class TestAuditTriggerInsert:
    """Trigger INSERT — dodanie rekordu powinno zostać zalogowane."""

    def test_insert_creates_log_entry(self, repos):
        """Po add() w repozytorium powinien pojawić się wpis INSERT w logu."""
        repos.set_audit_context("tester")

        record = EnergyConsumption(
            id=repos.energy_consumption.next_id(),
            year=2025, company="TestFirma A", amount=Decimal("100"),
            unit="MWh", source="test", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        ok, _ = repos.energy_consumption.add(record)
        assert ok is True

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        assert len(logs) == 1

        entry = logs[0]
        assert entry.change_type == "INSERT"
        assert entry.login == "tester"
        assert entry.table_name == "tbl_e_cons"
        assert entry.record_id == str(record.id)
        assert entry.previous_data is None
        assert entry.actual_data is not None

    def test_insert_actual_data_contains_record(self, repos):
        """actual_data powinno zawierać poprawny JSON z danymi rekordu."""
        repos.set_audit_context("tester")

        record = EnergyConsumption(
            id=repos.energy_consumption.next_id(),
            year=2025, company="TestFirma A", amount=Decimal("777"),
            unit="MWh", source="test_json", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        data = json.loads(logs[0].actual_data)
        assert data["amount"] == "777"
        assert data["company"] == "TestFirma A"
        assert data["energy_source"] == "Zakupiona"


class TestAuditTriggerUpdate:
    """Trigger UPDATE — edycja rekordu loguje stan przed i po zmianie."""

    def test_update_creates_log_entry(self, repos):
        """Po update() powinien pojawić się wpis UPDATE z previous i actual."""
        repos.set_audit_context("tester")

        ok, _ = repos.energy_consumption.update(1, {"amount": Decimal("999")})
        assert ok is True

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        assert len(logs) == 1

        entry = logs[0]
        assert entry.change_type == "UPDATE"
        assert entry.previous_data is not None
        assert entry.actual_data is not None

    def test_update_previous_and_actual_differ(self, repos):
        """previous_data i actual_data powinny zawierać różne wartości."""
        repos.set_audit_context("tester")

        repos.energy_consumption.update(1, {"amount": Decimal("999")})

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        previous = json.loads(logs[0].previous_data)
        actual = json.loads(logs[0].actual_data)
        assert previous["amount"] == "450"  # oryginalna wartość z conftest
        assert actual["amount"] == "999"


class TestAuditTriggerDelete:
    """Trigger DELETE — usunięcie rekordu loguje stan przed usunięciem."""

    def test_delete_creates_log_entry(self, repos):
        """Po delete() powinien pojawić się wpis DELETE z previous_data."""
        repos.set_audit_context("tester")

        ok, _ = repos.energy_consumption.delete(1)
        assert ok is True

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        assert len(logs) == 1

        entry = logs[0]
        assert entry.change_type == "DELETE"
        assert entry.table_name == "tbl_e_cons"
        assert entry.previous_data is not None
        assert entry.actual_data is None

    def test_delete_previous_data_contains_record(self, repos):
        """previous_data powinno zawierać dane usuniętego rekordu."""
        repos.set_audit_context("tester")

        repos.energy_consumption.delete(1)

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        data = json.loads(logs[0].previous_data)
        assert data["id"] == 1
        assert data["company"] == "TestFirma A"


# === Testy braku logowania bez kontekstu ===

class TestAuditWithoutContext:
    """Bez set_audit_context() zmiany NIE powinny być logowane."""

    def test_no_log_without_context(self, repos):
        """Bez aktywacji audytu — brak wpisów w logu."""
        record = EnergyConsumption(
            id=repos.energy_consumption.next_id(),
            year=2025, company="TestFirma A", amount=Decimal("100"),
            unit="MWh", source="test", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        assert len(logs) == 0


# === Testy filtrowania historii zmian ===

class TestChangeLogFiltering:
    """Testy metod filtrowania — get_by_table, get_by_record, get_by_user."""

    def _make_changes(self, repos):
        """Pomocnicza — tworzy kilka wpisów w logu z różnych tabel."""
        repos.set_audit_context("tester")

        # INSERT w tbl_e_cons
        record = EnergyConsumption(
            id=repos.energy_consumption.next_id(),
            year=2025, company="TestFirma A", amount=Decimal("100"),
            unit="MWh", source="test", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)

        # UPDATE w tbl_stationary_combustion
        repos.stationary.update(2, {"amount": Decimal("9999")})

        # Zmiana użytkownika
        repos.set_audit_context("admin1")
        repos.energy_consumption.update(1, {"amount": Decimal("500")})

        repos.change_log.reload()

    def test_get_by_table(self, repos):
        """Filtrowanie po nazwie tabeli."""
        self._make_changes(repos)
        logs = repos.change_log.get_by_table("tbl_e_cons")
        assert len(logs) == 2  # INSERT + UPDATE
        assert all(l.table_name == "tbl_e_cons" for l in logs)

    def test_get_by_record(self, repos):
        """Filtrowanie po konkretnym rekordzie w tabeli."""
        self._make_changes(repos)
        logs = repos.change_log.get_by_record("tbl_e_cons", "1")
        assert len(logs) == 1  # tylko UPDATE na id=1
        assert logs[0].change_type == "UPDATE"

    def test_get_by_user(self, repos):
        """Filtrowanie po loginie użytkownika."""
        self._make_changes(repos)
        tester_logs = repos.change_log.get_by_user("tester")
        admin_logs = repos.change_log.get_by_user("admin1")
        assert len(tester_logs) == 2
        assert len(admin_logs) == 1


# === Test pełnego cyklu życia rekordu ===

class TestAuditFullCycle:
    """Test pełnego cyklu INSERT → UPDATE → DELETE na jednym rekordzie."""

    def test_full_lifecycle(self, repos):
        """Cały cykl życia rekordu powinien być udokumentowany w logu."""
        repos.set_audit_context("tester")

        # INSERT
        new_id = repos.energy_consumption.next_id()
        record = EnergyConsumption(
            id=new_id, year=2025, company="TestFirma A",
            amount=Decimal("100"), unit="MWh", source="lifecycle",
            energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)

        # UPDATE
        repos.energy_consumption.update(new_id, {"amount": Decimal("200")})

        # DELETE
        repos.energy_consumption.delete(new_id)

        # Weryfikacja logu
        repos.change_log.reload()
        logs = repos.change_log.get_by_record("tbl_e_cons", str(new_id))
        assert len(logs) == 3

        assert logs[0].change_type == "INSERT"
        assert logs[1].change_type == "UPDATE"
        assert logs[2].change_type == "DELETE"

        # INSERT: brak previous, jest actual
        assert logs[0].previous_data is None
        assert json.loads(logs[0].actual_data)["amount"] == "100"

        # UPDATE: previous=100, actual=200
        assert json.loads(logs[1].previous_data)["amount"] == "100"
        assert json.loads(logs[1].actual_data)["amount"] == "200"

        # DELETE: previous=200, brak actual
        assert json.loads(logs[2].previous_data)["amount"] == "200"
        assert logs[2].actual_data is None

    def test_sequential_ids(self, repos):
        """ID w rejestrze zmian powinny rosnąć sekwencyjnie."""
        repos.set_audit_context("tester")

        new_id = repos.energy_consumption.next_id()
        record = EnergyConsumption(
            id=new_id, year=2025, company="TestFirma A",
            amount=Decimal("50"), unit="MWh", source="seq",
            energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)
        repos.energy_consumption.update(new_id, {"amount": Decimal("60")})
        repos.energy_consumption.delete(new_id)

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        ids = [l.id_rejestr_zmian for l in logs]
        assert ids == [1, 2, 3]

    def test_datetime_is_recorded(self, repos):
        """Każdy wpis w logu powinien mieć datę i godzinę."""
        repos.set_audit_context("tester")

        record = EnergyConsumption(
            id=repos.energy_consumption.next_id(),
            year=2025, company="TestFirma A", amount=Decimal("50"),
            unit="MWh", source="dt", energy_source="Zakupiona",
            energy_type="Energia elektryczna nie OZE",
        )
        repos.energy_consumption.add(record)

        repos.change_log.reload()
        logs, _ = repos.change_log.get_all()
        assert isinstance(logs[0].date_change, datetime)
        assert logs[0].date_change.year >= 2025
