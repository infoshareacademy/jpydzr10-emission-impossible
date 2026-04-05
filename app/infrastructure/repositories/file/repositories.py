import os
from decimal import Decimal
from typing import Optional

from app.application.class_models import (
    Company, StationaryCombustion, MobileCombustion, ProcessEmission,
    FugitiveEmission, EmissionFactor, UnitConverter, UserAuthorization,
    EnergyConsumption, EnergyPurchased, UserPermission, ChangeLog,
    ReductionTarget, EmailLog,
)
from app.infrastructure.repositories.file.csv_repository import CsvRepository

# Domyślna ścieżka — można nadpisać zmienną środowiskową
FOLDER_PATH = os.getenv("DATA_FOLDER", "data_files")

class CompanyRepository(CsvRepository[Company]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=Company,
            file_path=os.path.join(folder, "tbl_companies.csv"),
            id_field="co_id",
        )

    def get_by_name(self, name: str) -> Optional[Company]:
        objects, _ = self.get_all()
        for obj in objects:
            if obj.co_name.lower() == name.strip().lower():
                return obj
        return None

    def get_by_group(self, group_name: str) -> list[Company]:
        objects, _ = self.get_all()
        return [o for o in objects if o.cg_name.lower() == group_name.strip().lower()]

    def get_groups(self) -> list[str]:
        objects, _ = self.get_all()
        return sorted(set(o.cg_name for o in objects))

class StationaryCombustionRepository(CsvRepository[StationaryCombustion]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=StationaryCombustion,
            file_path=os.path.join(folder, "tbl_stationary_combustion.csv"),
        )

    def get_for_report(self, year: int, company: str) -> list[StationaryCombustion]:
        return [r for r in self.get_filtered(year=year, company=company) if r.raport]


class MobileCombustionRepository(CsvRepository[MobileCombustion]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=MobileCombustion,
            file_path=os.path.join(folder, "tbl_mobile_combustion.csv"),
        )


class ProcessEmissionRepository(CsvRepository[ProcessEmission]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=ProcessEmission,
            file_path=os.path.join(folder, "tbl_process_emissions.csv"),
        )


class FugitiveEmissionRepository(CsvRepository[FugitiveEmission]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=FugitiveEmission,
            file_path=os.path.join(folder, "tbl_fugitve_emissions.csv"),
        )

class FactorRepository(CsvRepository[EmissionFactor]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=EmissionFactor,
            file_path=os.path.join(folder, "tbl_factors.csv"),
        )

    def get_factor(self, name_part: str, country: Optional[str] = None) -> Optional[EmissionFactor]:
        objects, _ = self.get_all()
        name_lower = name_part.strip().lower()
        for obj in objects:
            if name_lower in obj.factor_name.lower():
                if country is None or obj.country.lower() == country.strip().lower():
                    return obj
        return None

class AuthorisationRepository(CsvRepository[UserAuthorization]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=UserAuthorization,
            file_path=os.path.join(folder, "tbl_authorisations.csv"),
        )

    def get_companies_for_user(self, login: str, read_only: bool = True) -> list[str]:
        records = self.get_filtered(login=login)
        if read_only:
            return [r.company for r in records if r.read]
        return [r.company for r in records if r.save]


class ConverterRepository(CsvRepository[UnitConverter]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=UnitConverter,
            file_path=os.path.join(folder, "tbl_converters.csv"),
        )

    def convert(self, amount: Decimal, unit_from: str, unit_to: str) -> Decimal:
        if unit_from == unit_to:
            return amount

        objects, _ = self.get_all()

        for conv in objects:
            if conv.unit_from == unit_from and conv.unit_to == unit_to:
                return amount * conv.factor

        for conv in objects:
            if conv.unit_from == unit_to and conv.unit_to == unit_from:
                return amount / conv.factor

        raise ValueError(
            f"Brak przelicznika z '{unit_from}' na '{unit_to}'. "
            f"Dodaj wpis do tbl_converters.csv."
        )

# Nowe klasy repozytoriów
class EnergyConsumptionRepository(CsvRepository[EnergyConsumption]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=EnergyConsumption,
            file_path=os.path.join(folder, "tbl_e_cons.csv"),
        )

class EnergyPurchasedRepository(CsvRepository[EnergyPurchased]):
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=EnergyPurchased,
            file_path=os.path.join(folder, "tbl_e_purc.csv"),
        )

class PermissionRepository(CsvRepository[UserPermission]):
    """Repozytorium ról użytkowników (admin / użytkownik)."""
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=UserPermission,
            file_path=os.path.join(folder, "tbl_permissions.csv"),
        )

    def get_role(self, login: str) -> str:
        """Zwraca rolę użytkownika. Domyślnie 'użytkownik' jeśli brak wpisu."""
        records = self.get_filtered(login=login)
        if records:
            return records[0].role
        return "użytkownik"

    def is_admin(self, login: str) -> bool:
        return self.get_role(login) == "admin"


class ReductionTargetRepository(CsvRepository[ReductionTarget]):
    """Repozytorium celów redukcji emisji."""
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=ReductionTarget,
            file_path=os.path.join(folder, "tbl_reduction_targets.csv"),
        )

    def get_for_company(self, company: str) -> list[ReductionTarget]:
        """Zwraca cele redukcji dla danej firmy."""
        return self.get_filtered(company=company)


class ChangeLogRepository(CsvRepository[ChangeLog]):
    """Repozytorium rejestru zmian (audit log).

    Działa jak tabela audit — tylko zapis (add) i odczyt.
    Nie pozwala na update ani delete — zapewnia integralność logu.
    Backup wyłączony — sam log jest kopią historii zmian.
    """
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=ChangeLog,
            file_path=os.path.join(folder, "tbl_change_log.csv"),
            id_field="id_rejestr_zmian",
            backup=False,
        )

    def update(self, record_id, updates: dict) -> tuple[bool, str]:
        """Zablokowane — rejestr zmian jest niezmienny (immutable)."""
        return False, "Rejestr zmian nie pozwala na edycję rekordów"

    def delete(self, record_id) -> tuple[bool, str]:
        """Zablokowane — rejestr zmian jest niezmienny (immutable)."""
        return False, "Rejestr zmian nie pozwala na usuwanie rekordów"

    def get_by_table(self, table_name: str) -> list[ChangeLog]:
        """Zwraca historię zmian dla danej tabeli."""
        return self.get_filtered(table_name=table_name)

    def get_by_record(self, table_name: str, record_id: str) -> list[ChangeLog]:
        """Zwraca historię zmian konkretnego rekordu."""
        return self.get_filtered(table_name=table_name, record_id=record_id)

    def get_by_user(self, login: str) -> list[ChangeLog]:
        """Zwraca wszystkie zmiany wykonane przez danego użytkownika."""
        return self.get_filtered(login=login)


class EmailLogRepository(CsvRepository[EmailLog]):
    """Repozytorium rejestru wysłanych wiadomości e-mail.

    Tylko zapis i odczyt — historia komunikacji z osobami odpowiedzialnymi za dane.
    Bez backupu — sam log jest historią.
    """
    def __init__(self, folder: str = FOLDER_PATH):
        super().__init__(
            model_class=EmailLog,
            file_path=os.path.join(folder, "tbl_email_log.csv"),
            backup=False,
        )

    def update(self, record_id, updates: dict) -> tuple[bool, str]:
        """Zablokowane — rejestr e-mail jest niezmienny."""
        return False, "Rejestr e-mail nie pozwala na edycję rekordów"

    def delete(self, record_id) -> tuple[bool, str]:
        """Zablokowane — rejestr e-mail jest niezmienny."""
        return False, "Rejestr e-mail nie pozwala na usuwanie rekordów"

    def get_by_company(self, company: str) -> list[EmailLog]:
        """Zwraca historię maili dla danej spółki."""
        return self.get_filtered(company=company)

    def get_by_sender(self, sender: str) -> list[EmailLog]:
        """Zwraca maile wysłane przez danego użytkownika."""
        return self.get_filtered(sender=sender)


class RepositoryFactory:
    def __init__(self, folder: str = FOLDER_PATH):
        self.folder = folder
        self.change_log = ChangeLogRepository(folder)
        self.companies = CompanyRepository(folder)
        self.stationary = StationaryCombustionRepository(folder)
        self.mobile = MobileCombustionRepository(folder)
        self.process = ProcessEmissionRepository(folder)
        self.fugitive = FugitiveEmissionRepository(folder)
        self.factors = FactorRepository(folder)
        self.converters = ConverterRepository(folder)
        # Nowe repozytoria dla energii
        self.energy_consumption = EnergyConsumptionRepository(folder)
        self.energy_purchased = EnergyPurchasedRepository(folder)
        self.authorisations = AuthorisationRepository(folder)
        self.permissions = PermissionRepository(folder)
        self.reduction_targets = ReductionTargetRepository(folder)
        self.email_log = EmailLogRepository(folder)

    def set_audit_context(self, login: str):
        """Włącza audit log (trigger) dla wszystkich repozytoriów.

        Wywołaj po zalogowaniu użytkownika — od tego momentu każda zmiana
        (add/update/delete) w dowolnym repo będzie rejestrowana w tbl_change_log.csv.
        """
        for name in vars(self):
            attr = getattr(self, name)
            # Podpinamy audit do wszystkich repo OPRÓCZ samego change_log
            if isinstance(attr, CsvRepository) and not isinstance(attr, ChangeLogRepository):
                attr.set_audit_context(self.change_log, login)

    def reload_all(self):
        for name in vars(self):
            attr = getattr(self, name)
            if isinstance(attr, CsvRepository):
                attr.reload()

    def validate_all(self) -> dict[str, list[str]]:
        report = {}
        repo_names = [
            "companies", "stationary", "mobile", "process", "fugitive", "factors", "converters"
        ]
        for name in repo_names:
            repo = getattr(self, name)
            _, errors = repo.get_all()
            if errors:
                report[name] = errors
        return report