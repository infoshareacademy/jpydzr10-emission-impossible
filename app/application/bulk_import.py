"""
Hurtowy import danych emisyjnych z plików Excel (.xlsx) i CSV.

Obsługuje import rekordów do dowolnej tabeli emisyjnej:
- Walidacja Pydantic każdego wiersza
- Automatyczne nadawanie ID (next_id)
- Raport błędów — które wiersze nie przeszły walidacji
- Obsługa zarówno plików CSV jak i Excel (openpyxl)
"""

import csv
import os
from decimal import Decimal, InvalidOperation
from typing import Optional
from pydantic import ValidationError

from app.application.class_models import (
    StationaryCombustion, MobileCombustion, FugitiveEmission,
    ProcessEmission, EnergyConsumption,
)

TABLE_MODELS = {
    "stationary": StationaryCombustion,
    "mobile": MobileCombustion,
    "fugitive": FugitiveEmission,
    "process": ProcessEmission,
    "energy_consumption": EnergyConsumption,
}

SKIP_FIELDS = {"id"}

def _read_csv_rows(file_path: str) -> list[dict]:
    """Wczytuje wiersze z pliku CSV."""
    rows = []
    with open(file_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=_detect_delimiter(file_path))
        for row in reader:
            cleaned = {k.strip(): v.strip() if isinstance(v, str) else v
                       for k, v in row.items() if k}
            rows.append(cleaned)
    return rows


def _detect_delimiter(file_path: str) -> str:
    """Wykrywa separator CSV (średnik lub przecinek)."""
    with open(file_path, encoding="utf-8-sig") as f:
        first_line = f.readline()
    if ";" in first_line and "," not in first_line:
        return ";"
    if first_line.count(";") > first_line.count(","):
        return ";"
    return ","


def _read_excel_rows(file_path: str, sheet_name: Optional[str] = None) -> list[dict]:
    """Wczytuje wiersze z pliku Excel (.xlsx)."""
    from openpyxl import load_workbook

    wb = load_workbook(file_path, read_only=True, data_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    rows_iter = ws.iter_rows(values_only=True)
    headers = [str(h).strip() if h else "" for h in next(rows_iter)]

    rows = []
    for row_values in rows_iter:
        row = {}
        for h, v in zip(headers, row_values):
            if not h:
                continue
            if v is None:
                row[h] = ""
            elif isinstance(v, float):
                row[h] = str(Decimal(str(v)))
            else:
                row[h] = str(v).strip()
        rows.append(row)

    wb.close()
    return rows


def _parse_value(value: str):
    """Parsuje wartość z CSV/Excel — puste stringi → None."""
    if value == "" or value is None:
        return None
    return value


def bulk_import(file_path: str, repo_name: str, repo,
                sheet_name: Optional[str] = None) -> dict:
    """Importuje rekordy z pliku CSV lub Excel do repozytorium.

    Args:
        file_path: ścieżka do pliku .csv lub .xlsx
        repo_name: nazwa repozytorium (klucz z TABLE_MODELS)
        repo: obiekt CsvRepository do zapisu
        sheet_name: nazwa arkusza (tylko dla Excel)

    Returns:
        dict z kluczami:
            imported: liczba zaimportowanych rekordów
            errors: lista błędów [(numer_wiersza, komunikat)]
            skipped: liczba pominiętych wierszy
    """
    if repo_name not in TABLE_MODELS:
        return {"imported": 0, "errors": [(0, f"Nieznana tabela: {repo_name}")], "skipped": 0}

    model_class = TABLE_MODELS[repo_name]
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".xlsx", ".xls"):
        raw_rows = _read_excel_rows(file_path, sheet_name)
    elif ext == ".csv":
        raw_rows = _read_csv_rows(file_path)
    else:
        return {"imported": 0, "errors": [(0, f"Nieobsługiwany format: {ext}")], "skipped": 0}

    imported = 0
    errors = []
    skipped = 0

    for row_num, raw_row in enumerate(raw_rows, start=2):
        row = {k: _parse_value(v) for k, v in raw_row.items() if k.lower() not in SKIP_FIELDS}
        for field in ("amount", "emission_tco2eq", "factor"):
            if field in row and row[field] is not None:
                try:
                    row[field] = Decimal(str(row[field]))
                except (InvalidOperation, ValueError):
                    pass

        row["id"] = repo.next_id()

        try:
            record = model_class(**row)
        except ValidationError as e:
            for err in e.errors():
                field = " -> ".join(str(loc) for loc in err["loc"])
                errors.append((row_num, f"Pole '{field}': {err['msg']}"))
            skipped += 1
            continue
        except Exception as e:
            errors.append((row_num, f"Nieoczekiwany błąd: {e}"))
            skipped += 1
            continue

        ok, msg = repo.add(record)
        if ok:
            imported += 1
        else:
            errors.append((row_num, f"Błąd zapisu: {msg}"))
            skipped += 1

    return {"imported": imported, "errors": errors, "skipped": skipped}
