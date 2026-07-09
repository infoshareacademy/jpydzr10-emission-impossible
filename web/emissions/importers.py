"""
Scope 1 — Importery danych z pliku XLSX.

Architektura:
  BaseScope1Importer  ← logika wspólna (parsowanie, walidacja, sesja, zapis)
      ├── StationaryCombustionImporter
      ├── MobileCombustionImporter
      ├── ProcessEmissionImporter
      └── FugitiveEmissionImporter

Każdy importer:
  1. parse(file)              → weryfikuje nagłówki, parsuje wiersze
  2. to_session_payload()     → serializuje prawidłowe wiersze do JSON (sesja)
  3. save_from_payload(data)  → atomowy zapis do bazy (rollback przy błędzie)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Optional

import openpyxl

# ---------------------------------------------------------------------------
# Reprezentacja pojedynczego wiersza importu
# ---------------------------------------------------------------------------


@dataclass
class ImportRow:
    row_num: int
    raw: dict  # oryginalne wartości z pliku (string, dla wyświetlenia)
    data: dict  # sparsowane i zwalidowane wartości
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)


# ---------------------------------------------------------------------------
# Klasa bazowa
# ---------------------------------------------------------------------------


class BaseScope1Importer:
    """
    Abstrakcyjna klasa bazowa dla wszystkich importerów Scope 1.
    Podklasy implementują: _parse_row() oraz _instance_from_payload().
    """

    EXPECTED_HEADERS: list[str] = []
    MAX_ROWS: int = 500
    MAX_FILE_SIZE_MB: int = 5

    def __init__(self, company, user):
        self.company = company
        self.user = user
        self.rows: list[ImportRow] = []
        self.parse_errors: list[str] = []

    # ── Parsowanie pliku ────────────────────────────────────────────────────

    def parse(self, file_obj) -> bool:
        """
        Parsuje wgrany plik XLSX.
        Zwraca True jeśli struktura pliku jest poprawna (wiersze mogą mieć błędy).
        Zwraca False jeśli plik jest fundamentalnie zły (zły format, złe nagłówki itp.).
        """
        try:
            wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
        except Exception as exc:
            self.parse_errors.append(f"Nie można odczytać pliku XLSX: {exc}")
            return False

        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)

        # Walidacja nagłówków
        try:
            raw_header = next(rows_iter)
        except StopIteration:
            self.parse_errors.append("Plik jest całkowicie pusty.")
            return False

        actual_headers = [
            str(c).strip().lower() if c is not None else "" for c in raw_header
        ]
        expected = [h.lower() for h in self.EXPECTED_HEADERS]

        if actual_headers[: len(expected)] != expected:
            self.parse_errors.append(
                f"Nieprawidłowe nagłówki kolumn.\n"
                f"Oczekiwano:  {self.EXPECTED_HEADERS}\n"
                f"Otrzymano:   {actual_headers[: len(expected)]}"
            )
            return False

        # Zbieranie wierszy z danymi (pomijamy puste)
        data_rows = [r for r in rows_iter if any(v is not None for v in r)]

        if not data_rows:
            self.parse_errors.append(
                "Plik nie zawiera żadnych danych (poza wierszem nagłówkowym)."
            )
            return False

        if len(data_rows) > self.MAX_ROWS:
            self.parse_errors.append(
                f"Plik zawiera zbyt wiele wierszy ({len(data_rows):,}). "
                f"Maksymalna dozwolona liczba: {self.MAX_ROWS:,}. "
                f"Podziel dane na mniejsze pliki."
            )
            return False

        # Parsowanie wiersz po wierszu
        for idx, raw_row in enumerate(data_rows, start=2):  # row 2 = first data row
            n_cols = len(self.EXPECTED_HEADERS)
            padded = (list(raw_row) + [None] * n_cols)[:n_cols]
            self.rows.append(self._parse_row(idx, tuple(padded)))

        return True

    def _parse_row(self, row_num: int, cells: tuple) -> ImportRow:
        """Implementacja w podklasie."""
        raise NotImplementedError

    # ── Właściwości ─────────────────────────────────────────────────────────

    @property
    def valid_rows(self) -> list[ImportRow]:
        return [r for r in self.rows if r.is_valid]

    @property
    def invalid_rows(self) -> list[ImportRow]:
        return [r for r in self.rows if not r.is_valid]

    # ── Serializacja do sesji ───────────────────────────────────────────────

    def to_session_payload(self) -> list[dict]:
        """
        Serializuje prawidłowe wiersze do listy słowników JSON-safe.
        Przechowywane w sesji Django między krokiem podglądu a potwierdzeniem.
        """
        return [self._row_to_dict(r) for r in self.valid_rows]

    def _row_to_dict(self, row: ImportRow) -> dict:
        """Serializuje ImportRow do JSON-safe dict."""
        result = {"_row_num": row.row_num}
        for k, v in row.data.items():
            if isinstance(v, Decimal):
                result[k] = str(v)
            elif hasattr(v, "pk"):  # obiekt FK
                result[k] = v.pk
                result[f"{k}_display"] = str(v)
            elif v is None:
                result[k] = None
            else:
                result[k] = v
        return result

    # ── Atomowy zapis ───────────────────────────────────────────────────────

    def save_from_payload(self, payload: list[dict]) -> int:
        """
        Atomowo zapisuje wszystkie wiersze z sesji do bazy danych.
        Przy błędzie dowolnego wiersza — rollback całej transakcji.
        Zwraca liczbę zapisanych rekordów.
        """
        from calculator.calculation import calculate_record_emissions
        from django.db import transaction

        from .models import RecordStatus

        with transaction.atomic():
            count = 0
            for item in payload:
                row_num = item.get("_row_num", "?")
                try:
                    instance = self._instance_from_payload(item)
                    instance.company = self.company
                    instance.created_by = self.user
                    instance.updated_by = self.user
                    instance.status = RecordStatus.DRAFT

                    # Próba obliczenia emisji — nie blokuje importu przy braku wskaźnika
                    try:
                        calculate_record_emissions(instance)
                    except Exception:
                        instance.calculated_emission_tco2eq = None

                    instance.save()
                    count += 1

                except Exception as exc:
                    raise RuntimeError(
                        f"Błąd zapisu wiersza #{row_num}: {exc}"
                    ) from exc

        return count

    def _instance_from_payload(self, data: dict):
        """Tworzy (niezapisany) obiekt modelu z danych sesji. Implementacja w podklasie."""
        raise NotImplementedError

    # ── Walidatory pól ──────────────────────────────────────────────────────

    def _v_year(self, value, row: ImportRow) -> Optional[int]:
        """Waliduje rok (int, zakres 2010–2035)."""
        try:
            year = int(value)
        except (TypeError, ValueError):
            row.add_error(f"Rok '{value}' nie jest poprawną liczbą całkowitą.")
            return None
        if not (2010 <= year <= 2035):
            row.add_error(f"Rok {year} jest poza dozwolonym zakresem (2010–2035).")
            return None
        return year

    def _v_amount(self, value, row: ImportRow) -> Optional[Decimal]:
        """Waliduje ilość (Decimal > 0). Akceptuje przecinek lub kropkę dziesiętną."""
        if value is None:
            row.add_error("Brak wartości ilości.")
            return None
        try:
            normalized = str(value).replace(",", ".").strip()
            amount = Decimal(normalized)
        except (InvalidOperation, TypeError, AttributeError):
            row.add_error(f"Nieprawidłowa wartość ilości: '{value}'.")
            return None
        if amount <= 0:
            row.add_error(f"Ilość musi być większa od zera (podano: {value}).")
            return None
        return amount

    def _v_unit(self, value, row: ImportRow, allowed: list[str]) -> Optional[str]:
        """Waliduje jednostkę miary względem listy dozwolonych wartości."""
        if not value:
            row.add_error(f"Brak jednostki. Dozwolone: {', '.join(allowed)}.")
            return None
        v = str(value).strip()
        if v not in allowed:
            row.add_error(
                f"Jednostka '{v}' jest niedozwolona. "
                f"Dozwolone wartości: {', '.join(allowed)}."
            )
            return None
        return v

    def _v_text(
        self,
        value,
        label: str,
        row: ImportRow,
        max_len: int = 200,
        required: bool = True,
    ) -> Optional[str]:
        """Waliduje pole tekstowe."""
        text = str(value).strip() if value is not None else ""
        if not text:
            if required:
                row.add_error(f"Pole '{label}' jest wymagane.")
                return None
            return ""
        if len(text) > max_len:
            row.add_error(
                f"Pole '{label}' jest za długie ({len(text)} znaków, max: {max_len})."
            )
            return None
        return text

    def _v_fuel(self, value, row: ImportRow):
        """Wyszukuje FuelType po nazwie lub symbolu (case-insensitive)."""
        from calculator.models import FuelType

        if not value:
            row.add_error("Brak nazwy paliwa.")
            return None

        name = str(value).strip()

        # Szukamy po nazwie
        qs = FuelType.objects.filter(name__iexact=name)
        if qs.exists():
            return qs.first()

        # Fallback — szukamy po symbolu
        qs = FuelType.objects.filter(symbol__iexact=name)
        if qs.exists():
            return qs.first()

        row.add_error(
            f"Nieznane paliwo: '{name}'. "
            f"Sprawdź dostępne paliwa w słowniku (Paliwa → lista symboli/nazw)."
        )
        return None


# ---------------------------------------------------------------------------
# Importer — Spalanie stacjonarne
# ---------------------------------------------------------------------------


class StationaryCombustionImporter(BaseScope1Importer):
    EXPECTED_HEADERS = ["rok", "paliwo", "instalacja", "ilosc", "jednostka", "zrodlo"]
    ALLOWED_UNITS = ["m3", "Mg", "t", "kg", "MWh", "GJ"]
    EXAMPLE_ROW = [
        2023,
        "Gaz ziemny",
        "Kocioł nr 1 Hala A",
        1500.5,
        "m3",
        "Faktura 01/2023",
    ]
    INSTRUCTIONS = [
        "Rok: 2010–2035",
        "Paliwo: nazwa z bazy (np. Gaz ziemny, Węgiel kamienny, Olej napędowy (ON))",
        f"Jednostka: {', '.join(ALLOWED_UNITS)}",
    ]

    def _parse_row(self, row_num: int, cells: tuple) -> ImportRow:
        rok, paliwo, instalacja, ilosc, jednostka, zrodlo = cells
        raw = dict(zip(self.EXPECTED_HEADERS, cells))
        ir = ImportRow(row_num=row_num, raw=raw, data={})
        ir.data = {
            "year": self._v_year(rok, ir),
            "fuel": self._v_fuel(paliwo, ir),
            "installation": self._v_text(instalacja, "instalacja", ir),
            "amount": self._v_amount(ilosc, ir),
            "unit": self._v_unit(jednostka, ir, self.ALLOWED_UNITS),
            "source": self._v_text(zrodlo, "zrodlo", ir, required=False),
        }
        return ir

    def _instance_from_payload(self, data: dict):
        from .models import StationaryCombustion

        return StationaryCombustion(
            year=data["year"],
            fuel_id=data["fuel"],
            installation=data["installation"],
            amount=Decimal(data["amount"]),
            unit=data["unit"],
            source=data.get("source") or "",
        )


# ---------------------------------------------------------------------------
# Importer — Spalanie mobilne
# ---------------------------------------------------------------------------


class MobileCombustionImporter(BaseScope1Importer):
    EXPECTED_HEADERS = ["rok", "pojazd", "paliwo", "ilosc", "jednostka", "zrodlo"]
    ALLOWED_UNITS = ["l", "dm3", "m3", "kg"]
    EXAMPLE_ROW = [
        2023,
        "Samochód dostawczy VW Crafter",
        "Olej napędowy (ON)",
        850.0,
        "l",
        "Raport floty Q1 2023",
    ]
    INSTRUCTIONS = [
        "Rok: 2010–2035",
        "Pojazd: dowolny opis identyfikujący pojazd/flotę",
        "Paliwo: nazwa z bazy (np. Olej napędowy (ON), Benzyna (Pb95), LPG)",
        f"Jednostka: {', '.join(ALLOWED_UNITS)}",
    ]

    def _parse_row(self, row_num: int, cells: tuple) -> ImportRow:
        rok, pojazd, paliwo, ilosc, jednostka, zrodlo = cells
        raw = dict(zip(self.EXPECTED_HEADERS, cells))
        ir = ImportRow(row_num=row_num, raw=raw, data={})
        ir.data = {
            "year": self._v_year(rok, ir),
            "vehicle": self._v_text(pojazd, "pojazd", ir),
            "fuel": self._v_fuel(paliwo, ir),
            "amount": self._v_amount(ilosc, ir),
            "unit": self._v_unit(jednostka, ir, self.ALLOWED_UNITS),
            "source": self._v_text(zrodlo, "zrodlo", ir, required=False),
        }
        return ir

    def _instance_from_payload(self, data: dict):
        from .models import MobileCombustion

        return MobileCombustion(
            year=data["year"],
            vehicle=data["vehicle"],
            fuel_id=data["fuel"],
            amount=Decimal(data["amount"]),
            unit=data["unit"],
            source=data.get("source") or "",
        )


# ---------------------------------------------------------------------------
# Importer — Emisje procesowe
# ---------------------------------------------------------------------------


class ProcessEmissionImporter(BaseScope1Importer):
    EXPECTED_HEADERS = ["rok", "proces", "produkt", "ilosc", "jednostka", "zrodlo"]
    ALLOWED_UNITS = ["t", "Mg", "kg", "m3"]
    EXAMPLE_ROW = [
        2023,
        "Synteza amoniaku",
        "Amoniak NH3",
        250.0,
        "t",
        "Raport technologiczny 2023",
    ]
    INSTRUCTIONS = [
        "Rok: 2010–2035",
        "Proces: nazwa procesu technologicznego",
        "Produkt: nazwa produktu/substratu emitującego GHG",
        f"Jednostka: {', '.join(ALLOWED_UNITS)}",
    ]

    def _parse_row(self, row_num: int, cells: tuple) -> ImportRow:
        rok, proces, produkt, ilosc, jednostka, zrodlo = cells
        raw = dict(zip(self.EXPECTED_HEADERS, cells))
        ir = ImportRow(row_num=row_num, raw=raw, data={})
        ir.data = {
            "year": self._v_year(rok, ir),
            "process": self._v_text(proces, "proces", ir),
            "product": self._v_text(produkt, "produkt", ir),
            "amount": self._v_amount(ilosc, ir),
            "unit": self._v_unit(jednostka, ir, self.ALLOWED_UNITS),
            "source": self._v_text(zrodlo, "zrodlo", ir, required=False),
        }
        return ir

    def _instance_from_payload(self, data: dict):
        from .models import ProcessEmission

        return ProcessEmission(
            year=data["year"],
            process=data["process"],
            product=data["product"],
            amount=Decimal(data["amount"]),
            unit=data["unit"],
            source=data.get("source") or "",
        )


# ---------------------------------------------------------------------------
# Importer — Emisje niezorganizowane (fugitive)
# ---------------------------------------------------------------------------


class FugitiveEmissionImporter(BaseScope1Importer):
    EXPECTED_HEADERS = ["rok", "instalacja", "czynnik", "ilosc", "jednostka", "zrodlo"]
    ALLOWED_UNITS = ["kg", "g", "t"]
    EXAMPLE_ROW = [
        2023,
        "Klimatyzator biurowy nr 5",
        "R410A",
        2.5,
        "kg",
        "Karta Urządzenia 2023",
    ]
    INSTRUCTIONS = [
        "Rok: 2010–2035",
        "Instalacja: opis urządzenia/instalacji (klimatyzator, chłodnia itp.)",
        "Czynnik: nazwa czynnika chłodniczego/gazu (np. R410A, R134a, SF6)",
        f"Jednostka: {', '.join(ALLOWED_UNITS)}",
    ]

    def _parse_row(self, row_num: int, cells: tuple) -> ImportRow:
        rok, instalacja, czynnik, ilosc, jednostka, zrodlo = cells
        raw = dict(zip(self.EXPECTED_HEADERS, cells))
        ir = ImportRow(row_num=row_num, raw=raw, data={})
        ir.data = {
            "year": self._v_year(rok, ir),
            "installation": self._v_text(instalacja, "instalacja", ir),
            "product": self._v_text(czynnik, "czynnik", ir),
            "amount": self._v_amount(ilosc, ir),
            "unit": self._v_unit(jednostka, ir, self.ALLOWED_UNITS),
            "source": self._v_text(zrodlo, "zrodlo", ir, required=False),
        }
        return ir

    def _instance_from_payload(self, data: dict):
        from .models import FugitiveEmission

        return FugitiveEmission(
            year=data["year"],
            installation=data["installation"],
            product=data["product"],
            amount=Decimal(data["amount"]),
            unit=data["unit"],
            source=data.get("source") or "",
        )
