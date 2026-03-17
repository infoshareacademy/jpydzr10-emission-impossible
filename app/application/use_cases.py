"""
PRZEPŁYW:
    menu.py  →  use_cases.py  →  repositories.py  →  CSV files
                     ↕
            input_validators.py
"""

from decimal import Decimal
from typing import Optional
from decimal import ROUND_HALF_UP
from dotenv import load_dotenv

from app.infrastructure.repositories.file.repositories import RepositoryFactory
from app.application.class_models import StationaryCombustion, MobileCombustion, FugitiveEmission, FUEL_TYPES, MASS_UNITS, VOLUME_UNITS, MAX_YEAR, MIN_YEAR
from app.core.validators.input_validators import safe_input, safe_int, safe_decimal, safe_choice, safe_bool, confirm

load_dotenv()
class EmissionUseCases:
    def __init__(self, data_folder: str = "data_files"):
        self.repos = RepositoryFactory(data_folder)

    def display_table(self, repo_name: str, year: Optional[int] = None, company: Optional[str] = None):
        repo = getattr(self.repos, repo_name, None)
        if repo is None:
            print(f"Nieznane repozytorium: {repo_name}")
            return

        records, errors = repo.get_all()
        if errors:
            print("\nOstrzeżenia:")
            for err in errors:
                print(f"  {err}")

        if year:
            records = [r for r in records if hasattr(r, "year") and r.year == year]
        if company:
            records = [r for r in records if hasattr(r, "company") and r.company == company]

        if not records:
            print("Brak danych do wyświetlenia.")
            return

        fields = list(records[0].model_dump().keys())
        widths = {}
        for f in fields:
            max_val = max(len(str(getattr(r, f, ""))) for r in records)
            widths[f] = max(len(f), min(max_val, 25)) + 2

        header = "".join(f"{f:^{widths[f]}}" for f in fields)
        print(f"\n{header}")
        print("─" * len(header))

        for r in records:
            row = "".join(f"{str(getattr(r, f, '')):^{widths[f]}.{widths[f]}}" for f in fields)
            print(row)

        print(f"\nŁącznie: {len(records)} rekordów")

    def display_companies(self):
        companies, errors = self.repos.companies.get_all()
        if not companies:
            print("Brak firm w systemie.")
            return

        groups = self.repos.companies.get_groups()
        for group in groups:
            group_companies = self.repos.companies.get_by_group(group)
            print(f"\nGrupa: {group} ({len(group_companies)} spółek)")
            for c in group_companies:
                print(f"  [{c.co_id:>2}] {c.co_name:<25} {c.co_country:<15} {c.co_city}")

    def add_stationary_interactive(self) -> bool:
        print("\n─── Dodawanie: Spalanie stacjonarne ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        company = safe_input("Firma: ")
        if company is None: return False

        fuel = safe_choice("Paliwo: ", sorted(FUEL_TYPES))
        if fuel is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        if fuel in ("benzyna", "diesel", "LPG"):
            units = sorted(VOLUME_UNITS)
        else:
            units = sorted(MASS_UNITS | VOLUME_UNITS)
        unit = safe_choice("Jednostka: ", units)
        if unit is None: return False

        installation = safe_input("Instalacja: ")
        if installation is None: return False

        source = safe_input("Źródło danych: ", allow_empty=True) or ""
        raport = safe_bool("Uwzględnić w raporcie? ") or False

        print(f"\n  Rok: {year} | Firma: {company} | {fuel}: {amount} {unit}")
        print(f"  Instalacja: {installation} | Źródło: {source} | Raport: {'TAK' if raport else 'NIE'}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = StationaryCombustion(
            id=self.repos.stationary.next_id(), year=year, company=company,
            fuel=fuel, amount=amount, unit=unit, installation=installation,
            emission=Decimal("0"), source=source, raport=raport,
        )
        ok, msg = self.repos.stationary.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_mobile_interactive(self) -> bool:
        print("\n─── Dodawanie: Spalanie mobilne ───\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False
        company = safe_input("Firma: ")
        if company is None: return False
        vehicle = safe_input("Pojazd: ")
        if vehicle is None: return False
        fuel = safe_choice("Paliwo: ", sorted(FUEL_TYPES))
        if fuel is None: return False
        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False
        unit = safe_choice("Jednostka: ", sorted(VOLUME_UNITS))
        if unit is None: return False
        source = safe_input("Źródło: ", allow_empty=True) or ""

        if not confirm("\nZapisać? "):
            return False

        record = MobileCombustion(
            id=self.repos.mobile.next_id(), year=year, company=company,
            vehicle=vehicle, fuel=fuel, amount=amount, unit=unit, source=source,
        )
        ok, msg = self.repos.mobile.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def edit_record_interactive(self, repo_name: str) -> bool:
        repo = getattr(self.repos, repo_name, None)
        if repo is None:
            print(f"Nieznane repozytorium: {repo_name}")
            return False

        record_id = safe_int("ID rekordu: ", min_val=0)
        if record_id is None: return False

        record = repo.get_by_id(record_id)
        if record is None:
            print(f"Nie znaleziono ID {record_id}.")
            return False

        data = record.model_dump()
        editable = [k for k in data.keys() if k != repo.id_field]

        print("\nAktualne dane:")
        for i, field in enumerate(editable, 1):
            print(f"  {i}. {field}: {data[field]}")

        num = safe_int(f"Numer pola (1-{len(editable)}): ", 1, len(editable))
        if num is None: return False

        field_name = editable[num - 1]
        new_value = safe_input(f"Nowa wartość '{field_name}': ")
        if new_value is None: return False

        if not confirm(f"Zmienić '{field_name}' na '{new_value}'? "):
            return False

        ok, msg = repo.update(record_id, {field_name: new_value})
        print(f"{'Zaktualizowano!' if ok else f'Błąd: {msg}'}")
        return ok

    def delete_record_interactive(self, repo_name: str) -> bool:
        repo = getattr(self.repos, repo_name, None)
        if repo is None:
            return False

        record_id = safe_int("ID rekordu do usunięcia: ", min_val=0)
        if record_id is None: return False

        record = repo.get_by_id(record_id)
        if record is None:
            print(f"Nie znaleziono ID {record_id}.")
            return False

        print("\nRekord do usunięcia:")
        for k, v in record.model_dump().items():
            print(f"  {k}: {v}")

        if not confirm("\nUsunąć? "):
            return False

        ok, msg = repo.delete(record_id)
        print(f"{'Usunięto!' if ok else f'{msg}'}")
        return ok

    def calculate_scope_1(self, year: int, company: str, country: str = "Polska") -> bool:
        print(f"\n─── Rozpoczynam obliczenia Scope 1 dla: {company} ({year}) ───")
        success = True

        categories = [
            ("stationary", self.repos.stationary, "fuel"),
            ("mobile", self.repos.mobile, "fuel"),
            ("fugitive", self.repos.fugitive, "product"),
            ("process", self.repos.process, "process")
        ]

        for repo_name, repo, factor_key_field in categories:
            records = repo.get_filtered(year=year, company=company)
            if not records:
                continue

            print(f"Obliczanie: {repo_name} ({len(records)} rekordów)...")

            for record in records:
                factor_key_value = getattr(record, factor_key_field)
                factor_obj = self.repos.factors.get_factor(factor_key_value, country)
                if not factor_obj:
                    print(f"  [!] Brak wskaźnika emisji dla: '{factor_key_value}'. Pomijam rekord ID: {record.id}")
                    success = False
                    continue

                try:
                    if "/" in factor_obj.unit_factor:
                        num_unit, den_unit = factor_obj.unit_factor.split('/')
                    else:
                        num_unit = factor_obj.unit_factor
                        den_unit = record.unit

                    num_unit = num_unit.strip()
                    den_unit = den_unit.strip()

                    if "CO2" in num_unit.upper():
                        num_unit = "t" if "t" in num_unit.lower() else "kg"

                    converted_amount = self.repos.converters.convert(record.amount, record.unit, den_unit)

                    raw_emission = converted_amount * factor_obj.factor

                    final_emission_in_tonnes = self.repos.converters.convert(raw_emission, num_unit, "t")

                    ok, msg = repo.update(record.id, {"emission": final_emission_in_tonnes})
                    if not ok:
                        print(f"  [!] Błąd zapisu dla rekordu {record.id}: {msg}")
                        success = False

                except ValueError as e:
                    print(f"  [!] Błąd konwersji jednostek dla rekordu {record.id} ({factor_key_value}): {e}")
                    success = False
                except Exception as e:
                    print(f"  [!] Nieoczekiwany błąd (ID: {record.id}): {e}")
                    success = False

        print("─── Zakończono obliczenia ───\n")
        return success

    def generate_summary(self, year: int, company: str) -> dict:
        R = lambda d: d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        s = {
            "year": year, "company": company,
            "scope1_stationary": Decimal("0"),
            "scope1_mobile": Decimal("0"),
            "scope1_fugitive": Decimal("0"),
            "scope1_process": Decimal("0"),
            "total": Decimal("0"),
        }

        # Scope 1: spalanie stacjonarne (emisja podana w CSV)
        for r in self.repos.stationary.get_filtered(year=year, company=company):
            s["scope1_stationary"] += r.emission

        # Scope 1: emisje niezorganizowane
        for r in self.repos.fugitive.get_filtered(year=year, company=company):
            s["scope1_fugitive"] += r.emission

        # Scope 1: emisje procesowe
        for r in self.repos.process.get_filtered(year=year, company=company):
            s["scope1_process"] += r.emission

        # Scope 1: spalanie mobilne
        for r in self.repos.mobile.get_filtered(year=year, company=company):
            s["scope1_mobile"] += r.emission

        # Zaokrąglenie
        for k in s:
            if isinstance(s[k], Decimal):
                s[k] = R(s[k])
        s["total"] = sum(v for k, v in s.items() if k.startswith("scope"))
        return s

    def display_summary(self, year: int, company: str):
        s = self.generate_summary(year, company)
        print(f"\n{'═' * 55}")
        print(f" ŚLAD WĘGLOWY: {company}, rok {year}")
        print(f"{'═' * 55}")
        print(f" SCOPE 1 — emisje bezpośrednie:")
        print(f"   Spalanie stacjonarne:    {s['scope1_stationary']:>12} tCO2e")
        print(f"   Spalanie mobilne:        {s['scope1_mobile']:>12} tCO2e")
        print(f"   Emisje niezorganizowane: {s['scope1_fugitive']:>12} tCO2e")
        print(f"   Emisje procesowe:        {s['scope1_process']:>12} tCO2e")
        print(f"{'─' * 55}")
        print(f" ŁĄCZNIE:                   {s['total']:>12} tCO2e")
        print(f"{'═' * 55}")

    def validate_all_files(self):
        print("\n─── Walidacja plików ───\n")
        errors = self.repos.validate_all()
        if not errors:
            print("Wszystkie pliki poprawne!")
        else:
            for name, errs in errors.items():
                print(f"\n{name}:")
                for e in errs:
                    print(f" {e}")

    def get_company_context(self, year: int, company: str) -> str:
        summary = self.generate_summary(year, company)

        _, errors = self.repos.validate_all()
        company_errors = [e for e in errors.get("stationary", []) + errors.get("mobile", []) if company in e]

        context = f"""
        RAPORT EMISYJNY DLA: {company}
        ROK: {year}

        WYNIKI (w tonach CO2e):
        - Spalanie stacjonarne: {summary['scope1_stationary']}
        - Spalanie mobilne: {summary['scope1_mobile']}
        - Emisje niezorganizowane: {summary['scope1_fugitive']}
        - ŁĄCZNIE SCOPE 1: {summary['total']}

        PROBLEMY Z DANYMI:
        {", ".join(company_errors) if company_errors else "Brak błędów w danych."}

        WSKAZÓWKA: Jeśli wyniki są równe 0.000, może to oznaczać brak wskaźników emisji w tabeli factors.
        """
        return context