import os
from decimal import Decimal
from typing import Optional

from app.application.class_models import (
    Company, StationaryCombustion, MobileCombustion, ProcessEmission,
    FugitiveEmission, EmissionFactor, UnitConverter, UserAuthorization,
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
            id_field="login",
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


class RepositoryFactory:
    def __init__(self, folder: str = FOLDER_PATH):
        self.folder = folder
        self.companies = CompanyRepository(folder)
        self.stationary = StationaryCombustionRepository(folder)
        self.mobile = MobileCombustionRepository(folder)
        self.process = ProcessEmissionRepository(folder)
        self.fugitive = FugitiveEmissionRepository(folder)
        self.factors = FactorRepository(folder)
        self.converters = ConverterRepository(folder)
        self.authorisations = AuthorisationRepository(folder)

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