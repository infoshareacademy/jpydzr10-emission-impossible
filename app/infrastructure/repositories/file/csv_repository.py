import csv
import os
import shutil
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Generic, TypeVar, Type, Optional
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

class CsvRepository(Generic[T]):
    def __init__(
        self,
        model_class: Type[T],
        file_path: str,
        id_field: str = "id",
        backup: bool = True,
    ):
        self.model_class = model_class
        self.file_path = Path(file_path)
        self.id_field = id_field
        self.backup = backup
        self._cache: list[T] = []
        self._loaded: bool = False

    def get_all(self) -> tuple[list[T], list[str]]:
        if self._loaded:
            return self._cache.copy(), []

        if not self.file_path.exists():
            self._loaded = True
            return [], [f"Plik nie istnieje: {self.file_path}"]

        objects: list[T] = []
        errors: list[str] = []

        try:
            with open(self.file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        cleaned = self._clean_row(row)
                        obj = self.model_class(**cleaned)
                        objects.append(obj)

                    except ValidationError as e:
                        for err in e.errors():
                            field = " -> ".join(str(loc) for loc in err["loc"])
                            errors.append(
                                f"Wiersz {row_num}, pole '{field}': {err['msg']}"
                            )
                    except Exception as e:
                        errors.append(f"Wiersz {row_num}: nieoczekiwany błąd — {e}")

        except csv.Error as e:
            errors.append(f"Błąd parsowania CSV: {e}")
        except UnicodeDecodeError:
            errors.append("Błąd kodowania — plik musi być UTF-8")

        self._cache = objects
        self._loaded = True
        return objects.copy(), errors

    def get_by_id(self, record_id) -> Optional[T]:
        objects, _ = self.get_all()
        for obj in objects:
            if getattr(obj, self.id_field) == record_id:
                return obj
        return None

    def get_filtered(self, **filters) -> list[T]:
        objects, _ = self.get_all()
        result = []
        for obj in objects:
            match = True
            for field, value in filters.items():
                if not hasattr(obj, field) or getattr(obj, field) != value:
                    match = False
                    break
            if match:
                result.append(obj)
        return result

    def add(self, record: T) -> tuple[bool, str]:
        objects, _ = self.get_all()

        new_id = getattr(record, self.id_field)
        for obj in objects:
            if getattr(obj, self.id_field) == new_id:
                return False, f"Rekord z {self.id_field}={new_id} już istnieje"

        self._cache.append(record)
        success, msg = self._save_all()
        if not success:
            self._cache.pop()  # Cofnij jeśli zapis się nie udał
        return success, msg

    def update(self, record_id, updates: dict) -> tuple[bool, str]:
        objects, _ = self.get_all()

        for i, obj in enumerate(objects):
            if getattr(obj, self.id_field) == record_id:
                current_data = obj.model_dump()
                current_data.update(updates)
                try:
                    updated_obj = self.model_class(**current_data)
                except ValidationError as e:
                    msgs = "; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors())
                    return False, f"Błąd walidacji: {msgs}"

                self._cache[i] = updated_obj
                return self._save_all()

        return False, f"Nie znaleziono rekordu z {self.id_field}={record_id}"

    def delete(self, record_id) -> tuple[bool, str]:
        self.get_all()
        original_len = len(self._cache)
        self._cache = [
            obj for obj in self._cache
            if getattr(obj, self.id_field) != record_id
        ]

        if len(self._cache) == original_len:
            return False, f"Nie znaleziono rekordu z {self.id_field}={record_id}"

        return self._save_all()

    def next_id(self) -> int:
        objects, _ = self.get_all()
        if not objects:
            return 1
        max_id = max(getattr(obj, self.id_field) for obj in objects)
        return max_id + 1

    def _clean_row(self, row: dict) -> dict:
        cleaned = {}
        for key, value in row.items():
            key = key.strip()
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    value = None
            cleaned[key] = value
        return cleaned

    def _save_all(self) -> tuple[bool, str]:
        if not self._cache:
            return True, "Brak danych do zapisu"

        try:
            # Krok 1: Backup
            if self.backup and self.file_path.exists():
                self._create_backup()

            # Krok 2: Zapis do .tmp
            temp_path = self.file_path.with_suffix(".csv.tmp")
            fieldnames = list(self._cache[0].model_dump().keys())

            with open(temp_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for obj in self._cache:
                    row = obj.model_dump()
                    # Konwersja typów Pythona → string CSV
                    for key, value in row.items():
                        if isinstance(value, Decimal):
                            row[key] = str(value)
                        elif isinstance(value, bool):
                            row[key] = "TRUE" if value else "FALSE"
                        elif value is None:
                            row[key] = ""
                    writer.writerow(row)

            # Krok 3: Podmiana tmp
            temp_path.replace(self.file_path)
            return True, "Zapisano pomyślnie"

        except PermissionError:
            return False, f"Brak uprawnień do zapisu: {self.file_path}"
        except OSError as e:
            return False, f"Błąd systemu plików: {e}"

    def _create_backup(self):
        backup_dir = self.file_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.file_path.stem}_{timestamp}.csv"
        shutil.copy2(self.file_path, backup_dir / backup_name)

    def reload(self):
        self._cache = []
        self._loaded = False

    def __repr__(self) -> str:
        count = len(self._cache) if self._loaded else "?"
        return f"CsvRepository({self.model_class.__name__}, records={count})"