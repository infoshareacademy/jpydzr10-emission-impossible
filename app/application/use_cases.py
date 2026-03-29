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
from app.application.class_models import (
    StationaryCombustion, MobileCombustion, FugitiveEmission, ProcessEmission,
    EnergyConsumption, FUEL_TYPES, MASS_UNITS, VOLUME_UNITS, ENERGY_UNITS,
    ENERGY_SOURCE_TYPES, ENERGY_TYPES, MAX_YEAR, MIN_YEAR,
)
from app.core.validators.input_validators import safe_input, safe_int, safe_decimal, safe_choice, safe_bool, confirm

load_dotenv()
class EmissionUseCases:
    def __init__(self, data_folder: str = "data_files"):
        self.repos = RepositoryFactory(data_folder)

    def display_table(self, repo_name: str, year: Optional[int] = None,
                      company: Optional[str] = None,
                      allowed_companies: Optional[list[str]] = None):
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
        elif allowed_companies is not None:
            records = [r for r in records if hasattr(r, "company") and r.company in allowed_companies]

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

    def display_companies(self, allowed_companies: Optional[list[str]] = None):
        companies, errors = self.repos.companies.get_all()
        if allowed_companies is not None:
            companies = [c for c in companies if c.co_name in allowed_companies]
        if not companies:
            print("Brak firm do wyświetlenia.")
            return

        groups = sorted(set(c.cg_name for c in companies))
        for group in groups:
            group_companies = [c for c in companies if c.cg_name == group]
            print(f"\nGrupa: {group} ({len(group_companies)} spółek)")
            for c in group_companies:
                print(f"  [{c.co_id:>2}] {c.co_name:<25} {c.co_country:<15} {c.co_city}")

    def _choose_company_from_list(self, companies: list[str]) -> Optional[str]:
        """Wyświetla listę spółek do wyboru i zwraca wybraną nazwę lub None."""
        if not companies:
            print("Brak dostępnych spółek.")
            return None
        print(f"\n  Dostępne spółki:")
        for i, name in enumerate(companies, 1):
            print(f"    {i} │ {name}")
        raw = safe_input("Wybierz numer spółki: ")
        if raw is None:
            return None
        try:
            idx = int(raw)
            if 1 <= idx <= len(companies):
                return companies[idx - 1]
        except ValueError:
            pass
        print("Nieprawidłowy wybór.")
        return None

    def add_stationary_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        print("\n─── Dodawanie: Spalanie stacjonarne ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
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

    def add_mobile_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        print("\n─── Dodawanie: Spalanie mobilne ───\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False
        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
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

    def add_process_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie emisji procesowej — pola: process, product, amount, unit."""
        print("\n─── Dodawanie: Emisje procesowe ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        process = safe_input("Proces (np. kalcynacja, synteza): ")
        if process is None: return False

        product = safe_input("Produkt: ")
        if product is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(MASS_UNITS))
        if unit is None: return False

        source = safe_input("Źródło danych: ", allow_empty=True) or ""

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Proces: {process} | Produkt: {product} | {amount} {unit}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = ProcessEmission(
            id=self.repos.process.next_id(), year=year, company=company,
            process=process, product=product, amount=amount, unit=unit,
            emission=Decimal("0"), source=source,
        )
        ok, msg = self.repos.process.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_fugitive_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie emisji niezorganizowanej — pola: installation, product (czynnik chłodniczy), amount, unit."""
        print("\n─── Dodawanie: Emisje niezorganizowane ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        installation = safe_input("Instalacja (np. klimatyzacja biuro): ")
        if installation is None: return False

        product = safe_input("Czynnik chłodniczy (np. R410A, R32, R404A): ")
        if product is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(MASS_UNITS))
        if unit is None: return False

        source = safe_input("Źródło danych: ", allow_empty=True) or ""

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Instalacja: {installation} | Czynnik: {product} | {amount} {unit}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = FugitiveEmission(
            id=self.repos.fugitive.next_id(), year=year, company=company,
            installation=installation, product=product, amount=amount, unit=unit,
            emission=Decimal("0"), source=source,
        )
        ok, msg = self.repos.fugitive.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_energy_consumption_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie zużycia energii (Scope 2) — pola: energy_source, energy_type, amount, unit."""
        print("\n─── Dodawanie: Zużycie energii (Scope 2) ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        energy_source = safe_choice("Źródło energii: ", sorted(ENERGY_SOURCE_TYPES))
        if energy_source is None: return False

        energy_type = safe_choice("Typ energii: ", sorted(ENERGY_TYPES))
        if energy_type is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(ENERGY_UNITS))
        if unit is None: return False

        source = safe_input("Źródło danych (np. faktura): ", allow_empty=True) or ""

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Źródło: {energy_source} | Typ: {energy_type} | {amount} {unit}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EnergyConsumption(
            id=self.repos.energy_consumption.next_id(), year=year, company=company,
            energy_source=energy_source, energy_type=energy_type,
            amount=amount, unit=unit, emission=Decimal("0"), source=source,
        )
        ok, msg = self.repos.energy_consumption.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def _check_record_access(self, record, allowed_companies: Optional[list[str]]) -> bool:
        """Sprawdza czy rekord należy do spółki z listy dozwolonych.
        Obsługuje pole 'company' (tabele emisyjne) i 'co_name' (tabela firm)."""
        if allowed_companies is None:
            return True
        # Tabele emisyjne — pole 'company'
        if hasattr(record, "company"):
            if record.company not in allowed_companies:
                print(f"Brak uprawnień do rekordu — spółka '{record.company}' nie jest na liście Twoich spółek.")
                return False
            return True
        # Tabela firm — pole 'co_name'
        if hasattr(record, "co_name"):
            if record.co_name not in allowed_companies:
                print(f"Brak uprawnień do rekordu — spółka '{record.co_name}' nie jest na liście Twoich spółek.")
                return False
            return True
        return True

    def edit_record_interactive(self, repo_name: str, allowed_companies: Optional[list[str]] = None) -> bool:
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

        if not self._check_record_access(record, allowed_companies):
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

    def delete_record_interactive(self, repo_name: str, allowed_companies: Optional[list[str]] = None) -> bool:
        repo = getattr(self.repos, repo_name, None)
        if repo is None:
            return False

        record_id = safe_int("ID rekordu do usunięcia: ", min_val=0)
        if record_id is None: return False

        record = repo.get_by_id(record_id)
        if record is None:
            print(f"Nie znaleziono ID {record_id}.")
            return False

        if not self._check_record_access(record, allowed_companies):
            return False

        print("\nRekord do usunięcia:")
        for k, v in record.model_dump().items():
            print(f"  {k}: {v}")

        if not confirm("\nUsunąć? "):
            return False

        ok, msg = repo.delete(record_id)
        print(f"{'Usunięto!' if ok else f'{msg}'}")
        return ok

    def _get_records_in_range(self, repo, year_from: int, year_to: int, company: str) -> list:
        """Pobiera rekordy z repozytorium dla zakresu lat i firmy."""
        all_records = repo.get_filtered(company=company)
        return [r for r in all_records if year_from <= r.year <= year_to]

    def calculate_scope_1(self, year_from: int, year_to: int, company: str, country: str = "Polska") -> bool:
        years_label = str(year_from) if year_from == year_to else f"{year_from}–{year_to}"
        print(f"\n─── Rozpoczynam obliczenia Scope 1 dla: {company} ({years_label}) ───")
        success = True

        categories = [
            ("stationary", self.repos.stationary, "fuel"),
            ("mobile", self.repos.mobile, "fuel"),
            ("fugitive", self.repos.fugitive, "product"),
            ("process", self.repos.process, "process")
        ]

        for repo_name, repo, factor_key_field in categories:
            records = self._get_records_in_range(repo, year_from, year_to, company)
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

    def calculate_scope_2(self, year_from: int, year_to: int, company: str, country: str = "Polska") -> bool:
        """Oblicza emisje Scope 2 dla zużycia energii."""
        years_label = str(year_from) if year_from == year_to else f"{year_from}–{year_to}"
        print(f"\n─── Rozpoczynam obliczenia Scope 2 dla: {company} ({years_label}) ───")
        success = True

        # Pobieramy rekordy zużycia energii dla danej firmy i zakresu lat
        records = self._get_records_in_range(self.repos.energy_consumption, year_from, year_to, company)
        if not records:
            print("Brak danych o zużyciu energii.")
            return False

        print(f"Obliczanie: energy_consumption ({len(records)} rekordów)...")

        for record in records:
            # Szukamy wskaźnika emisji po typie energii
            factor_obj = self.repos.factors.get_factor(record.energy_type, country)

            if not factor_obj:
                print(f"  [!] Brak wskaźnika dla: '{record.energy_type}'. Pomijam ID: {record.id}")
                success = False
                continue

            try:
                # Ustalamy jednostkę mianownika ze wskaźnika
                if "/" in factor_obj.unit_factor:
                    num_unit, den_unit = factor_obj.unit_factor.split("/")
                    num_unit = num_unit.strip()
                    den_unit = den_unit.strip()
                else:
                    num_unit = factor_obj.unit_factor.strip()
                    den_unit = record.unit

                if "CO2" in num_unit.upper():
                    num_unit = "t" if "t" in num_unit.lower() else "kg"

                # Przeliczamy jednostki jeśli trzeba
                converted_amount = self.repos.converters.convert(
                    record.amount, record.unit, den_unit
                )

                # Obliczamy emisję
                raw_emission = converted_amount * factor_obj.factor

                # Przeliczamy wynik na tony
                final_emission = self.repos.converters.convert(raw_emission, num_unit, "t")

                # Zapisujemy wynik
                ok, msg = self.repos.energy_consumption.update(
                    record.id, {"emission": final_emission}
                )
                if not ok:
                    print(f"  [!] Błąd zapisu dla rekordu {record.id}: {msg}")
                    success = False

            except ValueError as e:
                print(f"  [!] Błąd konwersji dla rekordu {record.id}: {e}")
                success = False

        print("─── Zakończono obliczenia Scope 2 ───\n")
        return success

    def generate_summary(self, year_from: int, year_to: int, company: str) -> dict:
        R = lambda d: d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        years_label = str(year_from) if year_from == year_to else f"{year_from}–{year_to}"
        s = {
            "year_from": year_from, "year_to": year_to,
            "years_label": years_label, "company": company,
            "scope1_stationary": Decimal("0"),
            "scope1_mobile": Decimal("0"),
            "scope1_fugitive": Decimal("0"),
            "scope1_process": Decimal("0"),
            "scope2_energy": Decimal("0"),
            "total": Decimal("0"),
        }

        # Scope 1: spalanie stacjonarne
        for r in self._get_records_in_range(self.repos.stationary, year_from, year_to, company):
            s["scope1_stationary"] += r.emission

        # Scope 1: emisje niezorganizowane
        for r in self._get_records_in_range(self.repos.fugitive, year_from, year_to, company):
            s["scope1_fugitive"] += r.emission

        # Scope 1: emisje procesowe
        for r in self._get_records_in_range(self.repos.process, year_from, year_to, company):
            s["scope1_process"] += r.emission

        # Scope 1: spalanie mobilne
        for r in self._get_records_in_range(self.repos.mobile, year_from, year_to, company):
            s["scope1_mobile"] += r.emission

        # Scope 2: zużycie energii
        for r in self._get_records_in_range(self.repos.energy_consumption, year_from, year_to, company):
            s["scope2_energy"] += r.emission

        # Zaokrąglenie
        for k in s:
            if isinstance(s[k], Decimal):
                s[k] = R(s[k])
        s["total"] = sum(v for k, v in s.items() if k.startswith("scope"))
        return s

    def get_available_years(self, company: str) -> list[int]:
        """Pobiera posortowaną listę lat dla których istnieją dane danej spółki."""
        years = set()
        repos = [
            self.repos.stationary, self.repos.mobile,
            self.repos.fugitive, self.repos.process,
            self.repos.energy_consumption,
        ]
        for repo in repos:
            for r in repo.get_filtered(company=company):
                years.add(r.year)
        return sorted(years)

    def display_summary(self, year_from: int, year_to: int, company: str):
        s = self.generate_summary(year_from, year_to, company)
        available_years = self.get_available_years(company)
        # Filtruj do zakresu
        years_in_range = [y for y in available_years if year_from <= y <= year_to]
        if years_in_range:
            years_info = ", ".join(str(y) for y in years_in_range)
        else:
            years_info = "brak danych"
        print(f"\n{'═' * 55}")
        print(f" ŚLAD WĘGLOWY: {company}")
        print(f" Lata z danymi: {years_info}")
        print(f"{'═' * 55}")
        print(f" SCOPE 1 — emisje bezpośrednie:")
        print(f"   Spalanie stacjonarne:    {s['scope1_stationary']:>12} tCO2e")
        print(f"   Spalanie mobilne:        {s['scope1_mobile']:>12} tCO2e")
        print(f"   Emisje niezorganizowane: {s['scope1_fugitive']:>12} tCO2e")
        print(f"   Emisje procesowe:        {s['scope1_process']:>12} tCO2e")
        print(f"{'─' * 55}")
        print(f" SCOPE 2 — energia pośrednia:")
        print(f"   Zużycie energii:         {s['scope2_energy']:>12} tCO2e")
        print(f"{'═' * 55}")
        print(f" ŁĄCZNIE (Scope 1 + 2):     {s['total']:>12} tCO2e")
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

    def is_admin(self, login: str) -> bool:
        """Sprawdza czy użytkownik ma rolę admina."""
        return self.repos.permissions.is_admin(login)

    def get_user_role(self, login: str) -> str:
        """Zwraca rolę użytkownika."""
        return self.repos.permissions.get_role(login)

    def get_user_companies(self, login: str, read_only: bool = True) -> list[str]:
        # Admin ma dostęp do wszystkich spółek
        if self.is_admin(login):
            companies, _ = self.repos.companies.get_all()
            return [c.co_name for c in companies]
        return self.repos.authorisations.get_companies_for_user(login, read_only)

    def display_summary_for_user(self, login: str, year_from: int, year_to: int):
        companies = self.get_user_companies(login)
        if not companies:
            print(f"Brak przypisanych spółek dla użytkownika '{login}'.")
            return

        years_label = str(year_from) if year_from == year_to else f"{year_from}–{year_to}"
        print(f"\n{'═' * 60}")
        print(f" PODSUMOWANIE DLA: {login} | {years_label}")
        print(f" Dostęp do {len(companies)} spółek")
        print(f"{'═' * 60}")

        grand_total = Decimal("0")
        for company in companies:
            s = self.generate_summary(year_from, year_to, company)
            total = s["total"]
            grand_total += total
            available = self.get_available_years(company)
            years_in_range = [y for y in available if year_from <= y <= year_to]
            years_info = ", ".join(str(y) for y in years_in_range) if years_in_range else "brak danych"
            print(f"\n  {company}  ({years_info})")
            print(f"    SCOPE 1:")
            print(f"      Spalanie stacjonarne:    {s['scope1_stationary']:>12} tCO2e")
            print(f"      Spalanie mobilne:        {s['scope1_mobile']:>12} tCO2e")
            print(f"      Emisje niezorganizowane: {s['scope1_fugitive']:>12} tCO2e")
            print(f"      Emisje procesowe:        {s['scope1_process']:>12} tCO2e")
            print(f"    SCOPE 2:")
            print(f"      Zużycie energii:         {s['scope2_energy']:>12} tCO2e")
            print(f"    {'─' * 48}")
            print(f"    RAZEM (Scope 1 + 2):       {total:>12} tCO2e")

        print(f"\n{'═' * 60}")
        print(f" ŁĄCZNIE WSZYSTKIE SPÓŁKI:  {grand_total:>12} tCO2e")
        print(f"{'═' * 60}")

    def verify_factors_and_converters(self, country: str = "Polska") -> list[dict]:
        """Sprawdza wszystkie tabele źródłowe pod kątem brakujących wskaźników i przeliczników.

        Zwraca listę słowników z kluczami:
            tabela_zrodlowa, id, info
        """
        issues = []

        # Scope 1: tabele emisyjne i ich pole klucza do wyszukiwania wskaźnika
        scope1_sources = [
            ("stationary", self.repos.stationary, "fuel"),
            ("mobile", self.repos.mobile, "fuel"),
            ("fugitive", self.repos.fugitive, "product"),
            ("process", self.repos.process, "process"),
        ]

        # Scope 2: zużycie energii
        scope2_sources = [
            ("energy_consumption", self.repos.energy_consumption, "energy_type"),
        ]

        all_sources = scope1_sources + scope2_sources

        for source_name, repo, factor_key_field in all_sources:
            records, _ = repo.get_all()
            for record in records:
                factor_key_value = getattr(record, factor_key_field)
                factor_obj = self.repos.factors.get_factor(factor_key_value, country)

                if not factor_obj:
                    issues.append({
                        "tabela_zrodlowa": source_name,
                        "id": record.id,
                        "info": f"Brak wskaźnika emisji dla: '{factor_key_value}' (kraj: {country})",
                    })
                    continue

                # Sprawdź czy przelicznik jednostek jest dostępny
                try:
                    if "/" in factor_obj.unit_factor:
                        num_unit, den_unit = factor_obj.unit_factor.split("/")
                        num_unit = num_unit.strip()
                        den_unit = den_unit.strip()
                    else:
                        num_unit = factor_obj.unit_factor.strip()
                        den_unit = record.unit

                    if "CO2" in num_unit.upper():
                        num_unit = "t" if "t" in num_unit.lower() else "kg"

                    # Sprawdź konwersję jednostki źródłowej → jednostka mianownika wskaźnika
                    if record.unit != den_unit:
                        self.repos.converters.convert(Decimal("1"), record.unit, den_unit)

                    # Sprawdź konwersję wyniku → tony
                    if num_unit != "t":
                        self.repos.converters.convert(Decimal("1"), num_unit, "t")

                except ValueError as e:
                    issues.append({
                        "tabela_zrodlowa": source_name,
                        "id": record.id,
                        "info": f"Brak przelicznika: {e}",
                    })

        return issues

    def display_verification_report(self, country: str = "Polska"):
        """Wyświetla raport weryfikacji wskaźników i przeliczników w terminalu."""
        print(f"\n─── Weryfikacja wskaźników i przeliczeń (kraj: {country}) ───\n")
        issues = self.verify_factors_and_converters(country)

        if not issues:
            print("  Wszystkie rekordy mają przypisane wskaźniki i przeliczniki. ✓")
            return

        # Nagłówki kolumn
        col_table = 22
        col_id = 8
        col_info = 60
        header = f"  {'TABELA':<{col_table}} {'ID':>{col_id}}  {'PROBLEM':<{col_info}}"
        print(header)
        print(f"  {'─' * col_table} {'─' * col_id}  {'─' * col_info}")

        for issue in issues:
            table = issue["tabela_zrodlowa"]
            rec_id = str(issue["id"])
            info = issue["info"]
            print(f"  {table:<{col_table}} {rec_id:>{col_id}}  {info}")

        print(f"\n  Łącznie problemów: {len(issues)}")

    def get_company_context(self, year: int, company: str) -> str:
        summary = self.generate_summary(year, year, company)

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