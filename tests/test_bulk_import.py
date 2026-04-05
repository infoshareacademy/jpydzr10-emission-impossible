"""Testy hurtowego importu danych z CSV i Excel."""

import csv
import os
import pytest
from decimal import Decimal

from app.application.bulk_import import bulk_import


class TestBulkImportCsv:
    """Testy importu z pliku CSV."""

    def test_import_stationary_csv(self, repos, tmp_path):
        """Import poprawnych rekordów spalania stacjonarnego z CSV."""
        csv_path = str(tmp_path / "import_stationary.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "year", "company", "data_quality", "amount", "unit", "source",
                "fuel", "installation",
            ])
            writer.writeheader()
            writer.writerow({
                "year": 2025, "company": "TestFirma A", "data_quality": "measured",
                "amount": "100", "unit": "m3", "source": "faktura",
                "fuel": "gaz ziemny", "installation": "kotlownia nowa",
            })
            writer.writerow({
                "year": 2025, "company": "TestFirma B", "data_quality": "estimated",
                "amount": "50", "unit": "t", "source": "szacunek",
                "fuel": "węgiel kamienny", "installation": "piec",
            })

        result = bulk_import(csv_path, "stationary", repos.stationary)
        assert result["imported"] == 2
        assert result["skipped"] == 0
        assert result["errors"] == []

    def test_import_skips_invalid_rows(self, repos, tmp_path):
        """Import pomija wiersze z błędami walidacji."""
        csv_path = str(tmp_path / "import_bad.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "year", "company", "amount", "unit", "source",
                "fuel", "installation",
            ])
            writer.writeheader()
            # Poprawny wiersz
            writer.writerow({
                "year": 2025, "company": "TestFirma A",
                "amount": "100", "unit": "m3", "source": "faktura",
                "fuel": "gaz ziemny", "installation": "piec",
            })
            # Błędny — nieznane paliwo
            writer.writerow({
                "year": 2025, "company": "TestFirma A",
                "amount": "100", "unit": "m3", "source": "faktura",
                "fuel": "NIEZNANE_PALIWO", "installation": "piec",
            })
            # Błędny — ujemna ilość
            writer.writerow({
                "year": 2025, "company": "TestFirma A",
                "amount": "-10", "unit": "m3", "source": "faktura",
                "fuel": "gaz ziemny", "installation": "piec",
            })

        result = bulk_import(csv_path, "stationary", repos.stationary)
        assert result["imported"] == 1
        assert result["skipped"] == 2
        assert len(result["errors"]) >= 2

    def test_import_detects_semicolon_separator(self, repos, tmp_path):
        """Import rozpoznaje separator ; w CSV."""
        csv_path = str(tmp_path / "import_semicolon.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "year", "company", "amount", "unit", "source",
                "vehicle", "fuel",
            ], delimiter=";")
            writer.writeheader()
            writer.writerow({
                "year": 2025, "company": "TestFirma A",
                "amount": "500", "unit": "l", "source": "karta",
                "vehicle": "samochód", "fuel": "diesel",
            })

        result = bulk_import(csv_path, "mobile", repos.mobile)
        assert result["imported"] == 1

    def test_import_unknown_table(self, repos, tmp_path):
        """Import do nieznanej tabeli zwraca błąd."""
        csv_path = str(tmp_path / "dummy.csv")
        with open(csv_path, "w") as f:
            f.write("a,b\n1,2\n")

        result = bulk_import(csv_path, "nieznana_tabela", repos.stationary)
        assert result["imported"] == 0
        assert len(result["errors"]) == 1

    def test_import_unsupported_format(self, repos, tmp_path):
        """Import z nieobsługiwanego formatu zwraca błąd."""
        txt_path = str(tmp_path / "dane.txt")
        with open(txt_path, "w") as f:
            f.write("dane\n")

        result = bulk_import(txt_path, "stationary", repos.stationary)
        assert result["imported"] == 0
        assert len(result["errors"]) == 1

    def test_import_assigns_auto_ids(self, repos, tmp_path):
        """Import automatycznie nadaje unikalne ID."""
        csv_path = str(tmp_path / "import_ids.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "year", "company", "amount", "unit", "source",
                "energy_source", "energy_type",
            ])
            writer.writeheader()
            writer.writerow({
                "year": 2025, "company": "TestFirma A",
                "amount": "100", "unit": "MWh", "source": "faktura",
                "energy_source": "Zakupiona", "energy_type": "Energia elektryczna nie OZE",
            })

        before = repos.energy_consumption.next_id()
        result = bulk_import(csv_path, "energy_consumption", repos.energy_consumption)
        assert result["imported"] == 1
        after = repos.energy_consumption.next_id()
        assert after == before + 1


class TestBulkImportExcel:
    """Testy importu z pliku Excel (.xlsx)."""

    def test_import_from_xlsx(self, repos, tmp_path):
        """Import poprawnych rekordów z pliku Excel."""
        from openpyxl import Workbook

        xlsx_path = str(tmp_path / "import_test.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append(["year", "company", "amount", "unit", "source",
                   "fuel", "installation"])
        ws.append([2025, "TestFirma A", 200, "m3", "faktura",
                   "gaz ziemny", "kotlownia import"])
        wb.save(xlsx_path)

        result = bulk_import(xlsx_path, "stationary", repos.stationary)
        assert result["imported"] == 1
        assert result["skipped"] == 0
