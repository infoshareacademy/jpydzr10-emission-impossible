"""
PRZEPŁYW:
    menu.py  →  use_cases.py  →  repositories.py  →  CSV files
                     ↕
            input_validators.py
"""

import os
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from dotenv import load_dotenv

from app.infrastructure.repositories.file.repositories import RepositoryFactory
from app.application.class_models import (
    StationaryCombustion, MobileCombustion, FugitiveEmission, ProcessEmission,
    EnergyConsumption, EnergyPurchased, EnergyProduced, EnergySold,
    Company, EmissionFactor, UnitConverter, UserAuthorization, UserPermission,
    ReductionTarget, FUEL_TYPES, MASS_UNITS, VOLUME_UNITS,
    ENERGY_UNITS, ENERGY_SOURCE_TYPES, ENERGY_TYPES, MAX_YEAR, MIN_YEAR,
    DATA_QUALITY_LEVELS, REDUCTION_STRATEGIES, USER_ROLES,
)
from app.core.validators.input_validators import (
    safe_input, safe_int, safe_decimal, safe_choice, safe_bool, confirm,
    safe_input_validated, validate_email, validate_phone,
    validate_nip, validate_regon, validate_krs,
)

load_dotenv()

# Ścieżka do folderu exportu
EXPORT_FOLDER = os.path.join("data_files", "export")

EMISSION_DEVIATION_THRESHOLD = Decimal("0.5")  # ±50% — próg ostrzeżenia


class EmissionUseCases:
    def __init__(self, data_folder: str = "data_files"):
        self.repos = RepositoryFactory(data_folder)

    def _calculate_emission_for_record(self, amount: Decimal, unit: str,
                                          factor_key: str, country: str = "Polska",
                                          year: Optional[int] = None) -> Decimal:
        """Oblicza emisję dla pojedynczego rekordu na podstawie wskaźnika emisji.

        Jeśli year podany — szuka wskaźnika z dokładnego roku (fallback na najnowszy).
        Jeśli year pominięty — używa najnowszego dostępnego wskaźnika.
        Zwraca emisję w tonach CO2e lub Decimal('0') jeśli brak wskaźnika.
        """
        factor_obj = self.repos.factors.get_factor(factor_key, country, year=year)
        if not factor_obj:
            return Decimal("0")
        try:
            if "/" in factor_obj.unit_factor:
                num_unit, den_unit = factor_obj.unit_factor.split("/")
                num_unit = num_unit.strip()
                den_unit = den_unit.strip()
            else:
                num_unit = factor_obj.unit_factor.strip()
                den_unit = unit

            if "CO2" in num_unit.upper():
                num_unit = "t" if "t" in num_unit.lower() else "kg"

            converted_amount = self.repos.converters.convert(amount, unit, den_unit)
            raw_emission = converted_amount * factor_obj.factor
            return self.repos.converters.convert(raw_emission, num_unit, "t")
        except (ValueError, Exception):
            return Decimal("0")

    def _check_emission_deviation(self, user_emission: Decimal, calc_emission: Decimal) -> bool:
        """Sprawdza odchylenie emisji deklarowanej od wyliczonej.

        Jeśli odchylenie > ±50%, wyświetla ostrzeżenie i pyta o potwierdzenie.
        Zwraca True jeśli użytkownik potwierdził lub brak odchylenia, False jeśli anulował.
        """
        if calc_emission <= 0:
            return True  # Brak wskaźnika — nie można porównać

        diff = user_emission - calc_emission
        pct = (diff / calc_emission * 100).quantize(Decimal("0.1"))

        if abs(diff / calc_emission) > EMISSION_DEVIATION_THRESHOLD:
            direction = "wyższa" if diff > 0 else "niższa"
            print(f"\n  ⚠ Wprowadzona emisja ({user_emission:.3f} tCO2eq) jest {abs(pct)}% {direction}")
            print(f"    niż wyliczona na podstawie domyślnych wskaźników ({calc_emission:.3f} tCO2eq).")
            return confirm("    Czy potwierdzasz poprawność przekazanych danych? ")
        return True

    def _collect_emission_fields(self, calc_emission: Decimal) -> Optional[dict]:
        """Zbiera od użytkownika pola: emission_tco2eq, raport, notes.

        Logika:
        - Pyta czy użytkownik ma własną wartość emisji
        - Jeśli tak → wymaga podania emission_tco2eq i raport, sprawdza odchylenie ±50%
        - Jeśli nie → emission_tco2eq=None, raport=None
        - notes — zawsze opcjonalne
        Zwraca dict z polami lub None jeśli anulowano.
        """
        has_emission = safe_bool("Masz własną wartość emisji? (tak/nie): ")
        if has_emission is None:
            return None

        emission_tco2eq = None
        raport = None

        if has_emission:
            if calc_emission > 0:
                print(f"  Szacowana emisja wg wskaźnika: {calc_emission:.3f} tCO2eq")
            emission_tco2eq = safe_decimal("Wartość emisji [tCO2eq]: ", min_val=Decimal("0"))
            if emission_tco2eq is None:
                return None

            # Sprawdź odchylenie ±50%
            if not self._check_emission_deviation(emission_tco2eq, calc_emission):
                print("Anulowano.")
                return None

            raport = safe_input("Źródło raportu emisji (np. KOBiZE, DEFRA, pomiar): ")
            if raport is None:
                return None

        notes = safe_input("Uwagi (opcjonalne): ", allow_empty=True) or None

        dq_raw = safe_input(
            "Pewność danych (measured/calculated/estimated, Enter = pomiń): ",
            allow_empty=True,
        )
        data_quality = dq_raw.strip().lower() if dq_raw else None
        if data_quality and data_quality not in DATA_QUALITY_LEVELS:
            print(f"  Nieznany poziom '{data_quality}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}")
            data_quality = None

        return {
            "emission_tco2eq": emission_tco2eq,
            "raport": raport,
            "notes": notes,
            "data_quality": data_quality,
        }

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

        calc_emission = self._calculate_emission_for_record(amount, unit, fuel, year=year)
        ef = self._collect_emission_fields(calc_emission)
        if ef is None: return False

        print(f"\n  Rok: {year} | Firma: {company} | {fuel}: {amount} {unit}")
        print(f"  Instalacja: {installation} | Źródło: {source}")
        if ef["emission_tco2eq"] is not None:
            print(f"  Emisja (deklarowana): {ef['emission_tco2eq']:.3f} tCO2eq | Raport: {ef['raport']}")
        else:
            print(f"  Emisja (zostanie obliczona z wskaźnika): ~{calc_emission:.3f} tCO2eq")
        if ef["notes"]:
            print(f"  Uwagi: {ef['notes']}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = StationaryCombustion(
            id=self.repos.stationary.next_id(), year=year, company=company,
            fuel=fuel, amount=amount, unit=unit, installation=installation,
            source=source, **ef,
        )
        ok, msg = self.repos.stationary.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_mobile_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        print("\n─── Dodawanie: Spalanie mobilne ───")
        print("(Wpisz 'q' aby anulować)\n")

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

        calc_emission = self._calculate_emission_for_record(amount, unit, fuel, year=year)
        ef = self._collect_emission_fields(calc_emission)
        if ef is None: return False

        print(f"\n  Rok: {year} | Firma: {company} | {vehicle} | {fuel}: {amount} {unit}")
        if ef["emission_tco2eq"] is not None:
            print(f"  Emisja (deklarowana): {ef['emission_tco2eq']:.3f} tCO2eq | Raport: {ef['raport']}")
        else:
            print(f"  Emisja (zostanie obliczona z wskaźnika): ~{calc_emission:.3f} tCO2eq")
        if ef["notes"]:
            print(f"  Uwagi: {ef['notes']}")

        if not confirm("\nZapisać? "):
            return False

        record = MobileCombustion(
            id=self.repos.mobile.next_id(), year=year, company=company,
            vehicle=vehicle, fuel=fuel, amount=amount, unit=unit, source=source,
            **ef,
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

        calc_emission = self._calculate_emission_for_record(amount, unit, process, year=year)
        ef = self._collect_emission_fields(calc_emission)
        if ef is None: return False

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Proces: {process} | Produkt: {product} | {amount} {unit}")
        if ef["emission_tco2eq"] is not None:
            print(f"  Emisja (deklarowana): {ef['emission_tco2eq']:.3f} tCO2eq | Raport: {ef['raport']}")
        else:
            print(f"  Emisja (zostanie obliczona z wskaźnika): ~{calc_emission:.3f} tCO2eq")
        if ef["notes"]:
            print(f"  Uwagi: {ef['notes']}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = ProcessEmission(
            id=self.repos.process.next_id(), year=year, company=company,
            process=process, product=product, amount=amount, unit=unit,
            source=source, **ef,
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

        calc_emission = self._calculate_emission_for_record(amount, unit, product, year=year)
        ef = self._collect_emission_fields(calc_emission)
        if ef is None: return False

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Instalacja: {installation} | Czynnik: {product} | {amount} {unit}")
        if ef["emission_tco2eq"] is not None:
            print(f"  Emisja (deklarowana): {ef['emission_tco2eq']:.3f} tCO2eq | Raport: {ef['raport']}")
        else:
            print(f"  Emisja (zostanie obliczona z wskaźnika): ~{calc_emission:.3f} tCO2eq")
        if ef["notes"]:
            print(f"  Uwagi: {ef['notes']}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = FugitiveEmission(
            id=self.repos.fugitive.next_id(), year=year, company=company,
            installation=installation, product=product, amount=amount, unit=unit,
            source=source, **ef,
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

        dq_raw = safe_input(
            "Pewność danych (measured/calculated/estimated, Enter = pomiń): ",
            allow_empty=True,
        )
        data_quality = dq_raw.strip().lower() if dq_raw else None
        if data_quality and data_quality not in DATA_QUALITY_LEVELS:
            print(f"  Nieznany poziom '{data_quality}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}")
            data_quality = None

        calc_emission = self._calculate_emission_for_record(amount, unit, energy_type, year=year)

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Źródło: {energy_source} | Typ: {energy_type} | {amount} {unit}")
        print(f"  Emisja (obliczona z wskaźnika): ~{calc_emission:.3f} tCO2e")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EnergyConsumption(
            id=self.repos.energy_consumption.next_id(), year=year, company=company,
            energy_source=energy_source, energy_type=energy_type,
            amount=amount, unit=unit, source=source, data_quality=data_quality,
        )
        ok, msg = self.repos.energy_consumption.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_energy_purchased_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie zakupionej energii (Scope 2) — pola: energy_type, amount, unit, trader, factor."""
        print("\n─── Dodawanie: Zakupiona energia (Scope 2) ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        energy_type = safe_choice("Typ energii: ", sorted(ENERGY_TYPES))
        if energy_type is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(ENERGY_UNITS))
        if unit is None: return False

        trader = safe_input("Dostawca energii: ", allow_empty=True) or ""
        source = safe_input("Źródło danych (np. faktura): ", allow_empty=True) or ""

        dq_raw = safe_input(
            "Pewność danych (measured/calculated/estimated, Enter = pomiń): ",
            allow_empty=True,
        )
        data_quality = dq_raw.strip().lower() if dq_raw else None
        if data_quality and data_quality not in DATA_QUALITY_LEVELS:
            print(f"  Nieznany poziom '{data_quality}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}")
            data_quality = None

        calc_emission = self._calculate_emission_for_record(amount, unit, energy_type, year=year)

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Typ: {energy_type} | {amount} {unit} | Dostawca: {trader or '—'}")
        print(f"  Emisja (obliczona z wskaźnika): ~{calc_emission:.3f} tCO2e")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EnergyPurchased(
            id=self.repos.energy_purchased.next_id(), year=year, company=company,
            energy_type=energy_type, amount=amount, unit=unit,
            trader=trader, factor=Decimal("0"), source=source, data_quality=data_quality,
        )
        ok, msg = self.repos.energy_purchased.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_energy_produced_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie wyprodukowanej energii (Scope 2) — pola: installation, energy_type, amount, unit."""
        print("\n─── Dodawanie: Wyprodukowana energia (Scope 2) ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        installation = safe_input("Nazwa instalacji: ", allow_empty=True) or ""

        energy_type = safe_choice("Typ energii: ", sorted(ENERGY_TYPES))
        if energy_type is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(ENERGY_UNITS))
        if unit is None: return False

        source = safe_input("Źródło danych (np. odczyt licznika): ", allow_empty=True) or ""

        dq_raw = safe_input(
            "Pewność danych (measured/calculated/estimated, Enter = pomiń): ",
            allow_empty=True,
        )
        data_quality = dq_raw.strip().lower() if dq_raw else None
        if data_quality and data_quality not in DATA_QUALITY_LEVELS:
            print(f"  Nieznany poziom '{data_quality}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}")
            data_quality = None

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Instalacja: {installation or '—'} | Typ: {energy_type} | {amount} {unit}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EnergyProduced(
            id=self.repos.energy_produced.next_id(), year=year, company=company,
            installation=installation, energy_type=energy_type,
            amount=amount, unit=unit, factor=Decimal("0"), source=source, data_quality=data_quality,
        )
        ok, msg = self.repos.energy_produced.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_energy_sold_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Dodawanie sprzedanej energii (Scope 2) — pola: energy_type, amount, unit, customer."""
        print("\n─── Dodawanie: Sprzedana energia (Scope 2) ───")
        print("(Wpisz 'q' aby anulować)\n")

        year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
        if year is None: return False

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        energy_type = safe_choice("Typ energii: ", sorted(ENERGY_TYPES))
        if energy_type is None: return False

        amount = safe_decimal("Ilość: ", min_val=Decimal("0"))
        if amount is None: return False

        unit = safe_choice("Jednostka: ", sorted(ENERGY_UNITS))
        if unit is None: return False

        customer = safe_input("Odbiorca energii: ", allow_empty=True) or ""
        source = safe_input("Źródło danych (np. umowa PPA): ", allow_empty=True) or ""

        dq_raw = safe_input(
            "Pewność danych (measured/calculated/estimated, Enter = pomiń): ",
            allow_empty=True,
        )
        data_quality = dq_raw.strip().lower() if dq_raw else None
        if data_quality and data_quality not in DATA_QUALITY_LEVELS:
            print(f"  Nieznany poziom '{data_quality}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}")
            data_quality = None

        print(f"\n  Rok: {year} | Firma: {company}")
        print(f"  Typ: {energy_type} | {amount} {unit} | Odbiorca: {customer or '—'}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EnergySold(
            id=self.repos.energy_sold.next_id(), year=year, company=company,
            energy_type=energy_type, amount=amount, unit=unit,
            customer=customer, source=source, data_quality=data_quality,
        )
        ok, msg = self.repos.energy_sold.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_company_interactive(self) -> bool:
        """Dodawanie nowej spółki do tbl_companies.csv.

        Każde pole jest walidowane na bieżąco — błędna wartość powoduje
        ponowne pytanie o to samo pole (nie dopiero na etapie zapisu).
        """
        print("\n─── Dodawanie: Spółka ───")
        print("(Wpisz 'q' aby anulować)\n")

        while True:
            co_name = safe_input("Nazwa spółki: ")
            if co_name is None: return False
            if self.repos.companies.exists_by_name(co_name):
                print(f"  ✗ Spółka '{co_name}' już istnieje w bazie danych.")
                continue
            break

        co_country = safe_input("Kraj: ")
        if co_country is None: return False

        co_city = safe_input("Miasto: ")
        if co_city is None: return False

        co_street = safe_input("Ulica i numer: ")
        if co_street is None: return False

        co_zip = safe_input("Kod pocztowy: ")
        if co_zip is None: return False

        co_tel = safe_input_validated("Telefon: ", validate_phone)
        if co_tel is None: return False

        co_mail = safe_input_validated("E-mail kontaktowy: ", validate_email)
        if co_mail is None: return False

        co_krs = safe_input_validated("KRS (10 cyfr): ", validate_krs)
        if co_krs is None: return False

        co_regon = safe_input_validated("REGON (9 lub 14 cyfr): ", validate_regon)
        if co_regon is None: return False

        co_nip = safe_input_validated("NIP (10 cyfr): ", validate_nip)
        if co_nip is None: return False

        cg_name = safe_input("Grupa kapitałowa: ")
        if cg_name is None: return False

        print(f"\n  Spółka: {co_name} | {co_city}, {co_country}")
        print(f"  NIP: {co_nip} | REGON: {co_regon} | KRS: {co_krs}")
        print(f"  Grupa: {cg_name}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = Company(
            co_id=self.repos.companies.next_id(),
            co_name=co_name, co_country=co_country, co_city=co_city,
            co_street=co_street, co_zip=co_zip, co_tel=co_tel,
            co_mail=co_mail, co_krs=co_krs, co_regon=co_regon,
            co_nip=co_nip, cg_name=cg_name,
        )
        ok, msg = self.repos.companies.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_factor_interactive(self) -> bool:
        """Dodawanie nowego wskaźnika emisji do tbl_factors.csv.

        Unikalność sprawdzana po (factor_name, country, year).
        """
        print("\n─── Dodawanie: Wskaźnik emisji ───")
        print("(Wpisz 'q' aby anulować)\n")

        factor_name = safe_input("Nazwa wskaźnika: ")
        if factor_name is None: return False

        country = safe_input("Kraj (np. Polska): ")
        if country is None: return False

        while True:
            year = safe_int("Rok obowiązywania wskaźnika: ", MIN_YEAR, MAX_YEAR)
            if year is None: return False
            if self.repos.factors.exists(factor_name, country, year):
                print(f"  ✗ Wskaźnik '{factor_name}' dla {country} w roku {year} już istnieje.")
                continue
            break

        factor = safe_decimal("Wartość wskaźnika: ", min_val=Decimal("0"))
        if factor is None: return False

        unit_factor = safe_input("Jednostka wskaźnika (np. tCO2e/MWh): ")
        if unit_factor is None: return False

        source = safe_input("Źródło (np. KOBiZE 2024, Enter = pomiń): ", allow_empty=True) or None

        print(f"\n  Wskaźnik: {factor_name} | {country} | {year}")
        print(f"  Wartość: {factor} {unit_factor} | Źródło: {source or '—'}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = EmissionFactor(
            id=self.repos.factors.next_id(),
            factor_name=factor_name, country=country, year=year,
            factor=factor, unit_factor=unit_factor, source=source,
        )
        ok, msg = self.repos.factors.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_converter_interactive(self) -> bool:
        """Dodawanie nowego przelicznika jednostek do tbl_converters.csv.

        Unikalność sprawdzana po (unit_from, unit_to).
        """
        print("\n─── Dodawanie: Przelicznik jednostek ───")
        print("(Wpisz 'q' aby anulować)\n")

        unit_from = safe_input("Jednostka źródłowa (np. MWh): ")
        if unit_from is None: return False

        while True:
            unit_to = safe_input("Jednostka docelowa (np. GJ): ")
            if unit_to is None: return False
            if self.repos.converters.exists(unit_from, unit_to):
                print(f"  ✗ Przelicznik '{unit_from}' → '{unit_to}' już istnieje.")
                continue
            break

        factor = safe_decimal("Mnożnik (unit_from × mnożnik = unit_to): ", min_val=Decimal("0.000001"))
        if factor is None: return False

        print(f"\n  Przelicznik: 1 {unit_from} = {factor} {unit_to}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = UnitConverter(
            id=self.repos.converters.next_id(),
            unit_from=unit_from, unit_to=unit_to, factor=factor,
        )
        ok, msg = self.repos.converters.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_authorisation_interactive(self) -> bool:
        """Dodawanie uprawnienia do spółki dla użytkownika (admin)."""
        print("\n─── Dodawanie: Uprawnienie spółki ───")
        print("(Wpisz 'q' aby anulować)\n")

        login = safe_input("Login użytkownika: ")
        if login is None: return False

        # Wyświetl dostępne spółki
        companies, _ = self.repos.companies.get_all()
        if companies:
            print(f"\n  Dostępne spółki:")
            for i, c in enumerate(companies, 1):
                print(f"    {i} │ {c.co_name}")
            raw = safe_input("Wybierz numer spółki lub wpisz nazwę: ")
            if raw is None: return False
            try:
                idx = int(raw)
                if 1 <= idx <= len(companies):
                    company = companies[idx - 1].co_name
                else:
                    company = raw
            except ValueError:
                company = raw
        else:
            company = safe_input("Nazwa spółki: ")
            if company is None: return False

        save_raw = safe_input("Uprawnienie zapisu (tak/nie): ", allow_empty=False)
        if save_raw is None: return False
        save = save_raw.strip().lower() in ("tak", "t", "yes", "1", "true")

        read_raw = safe_input("Uprawnienie odczytu (tak/nie): ", allow_empty=False)
        if read_raw is None: return False
        read = read_raw.strip().lower() in ("tak", "t", "yes", "1", "true")

        print(f"\n  Login: {login} | Spółka: {company}")
        print(f"  Zapis: {'TAK' if save else 'NIE'} | Odczyt: {'TAK' if read else 'NIE'}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = UserAuthorization(
            id=self.repos.authorisations.next_id(),
            login=login, company=company, save=save, read=read,
        )
        ok, msg = self.repos.authorisations.add(record)
        print(f"{'Zapisano!' if ok else f'Błąd: {msg}'}")
        return ok

    def add_permission_interactive(self) -> bool:
        """Dodawanie roli użytkownika (admin).

        Jeden użytkownik może mieć tylko jedną rolę — duplikat loginu jest blokowany.
        """
        print("\n─── Dodawanie: Rola użytkownika ───")
        print("(Wpisz 'q' aby anulować)\n")

        while True:
            login = safe_input("Login użytkownika: ")
            if login is None: return False
            if self.repos.permissions.exists(login):
                existing_role = self.repos.permissions.get_role(login)
                print(f"  ✗ Użytkownik '{login}' ma już przypisaną rolę: {existing_role}.")
                print(f"    Użyj opcji 'Edytuj rolę' aby ją zmienić.")
                continue
            break

        role = safe_choice("Rola: ", sorted(USER_ROLES))
        if role is None: return False

        print(f"\n  Login: {login} | Rola: {role}")

        if not confirm("\nZapisać? "):
            print("Anulowano.")
            return False

        record = UserPermission(
            id=self.repos.permissions.next_id(),
            login=login, role=role,
        )
        ok, msg = self.repos.permissions.add(record)
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

        updates = {field_name: new_value}

        # Jeśli użytkownik edytuje emission_tco2eq — wymagaj aktualizacji raport
        if field_name == "emission_tco2eq" and new_value.strip() != "":
            # Sprawdź odchylenie ±50% jeśli możliwe
            if hasattr(record, "amount") and hasattr(record, "unit"):
                factor_key = getattr(record, "fuel", None) or getattr(record, "product", None) or getattr(record, "process", None) or getattr(record, "energy_type", None)
                if factor_key:
                    calc = self._calculate_emission_for_record(record.amount, record.unit, factor_key, year=getattr(record, "year", None))
                    try:
                        user_em = Decimal(new_value)
                        if not self._check_emission_deviation(user_em, calc):
                            return False
                    except Exception:
                        pass

            raport_val = safe_input("Źródło raportu emisji (wymagane przy zmianie emisji): ")
            if raport_val is None: return False
            updates["raport"] = raport_val

        if not confirm(f"Zmienić '{field_name}' na '{new_value}'? "):
            return False

        ok, msg = repo.update(record_id, updates)
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
                # Pomiń rekordy z deklarowaną emisją — użytkownik podał własną wartość
                if record.emission_tco2eq is not None and record.emission_tco2eq > 0:
                    print(f"  [→] ID {record.id}: emisja deklarowana ({record.emission_tco2eq} tCO2eq) — pomijam obliczanie")
                    continue

                factor_key_value = getattr(record, factor_key_field)
                factor_obj = self.repos.factors.get_factor(factor_key_value, country, year=record.year)
                if not factor_obj:
                    print(f"  [!] Brak wskaźnika emisji dla: '{factor_key_value}' (rok {record.year}). Pomijam rekord ID: {record.id}")
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

                    ok, msg = repo.update(record.id, {"emission_tco2eq": final_emission_in_tonnes})
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
            # Szukamy wskaźnika emisji po typie energii i roku rekordu
            factor_obj = self.repos.factors.get_factor(record.energy_type, country, year=record.year)

            if not factor_obj:
                print(f"  [!] Brak wskaźnika dla: '{record.energy_type}' (rok {record.year}). Pomijam ID: {record.id}")
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
                    record.id, {"emission_tco2eq": final_emission}
                )
                if not ok:
                    print(f"  [!] Błąd zapisu dla rekordu {record.id}: {msg}")
                    success = False

            except ValueError as e:
                print(f"  [!] Błąd konwersji dla rekordu {record.id}: {e}")
                success = False

        print("─── Zakończono obliczenia Scope 2 ───\n")
        return success

    def _emission_or_calc(self, record, factor_key: str, country: str = "Polska") -> Decimal:
        """Zwraca emisję rekordu: deklarowaną (emission_tco2eq) jeśli podana, wyliczoną jeśli nie.

        Rok rekordu (record.year) jest przekazywany do get_factor() — wskaźnik
        dobierany jest dla tego samego roku co rekord emisyjny.
        """
        if record.emission_tco2eq is not None and record.emission_tco2eq > 0:
            return record.emission_tco2eq
        return self._calculate_emission_for_record(
            record.amount, record.unit, factor_key, country, year=record.year
        )

    def generate_summary(self, year_from: int, year_to: int, company: str,
                         country: str = "Polska") -> dict:
        """Generuje podsumowanie emisji — obliczenia wyłącznie w pamięci.
        Jeśli emission_tco2eq jest wypełnione → użyj deklarowanej wartości (priorytet).
        Jeśli puste → oblicz automatycznie z ilości × wskaźnik emisji."""
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
            s["scope1_stationary"] += self._emission_or_calc(r, r.fuel, country)

        # Scope 1: spalanie mobilne
        for r in self._get_records_in_range(self.repos.mobile, year_from, year_to, company):
            s["scope1_mobile"] += self._emission_or_calc(r, r.fuel, country)

        # Scope 1: emisje niezorganizowane
        for r in self._get_records_in_range(self.repos.fugitive, year_from, year_to, company):
            s["scope1_fugitive"] += self._emission_or_calc(r, r.product, country)

        # Scope 1: emisje procesowe
        for r in self._get_records_in_range(self.repos.process, year_from, year_to, company):
            s["scope1_process"] += self._emission_or_calc(r, r.process, country)

        # Scope 2: zużycie energii — zawsze oblicz (bez emission_tco2eq)
        for r in self._get_records_in_range(self.repos.energy_consumption, year_from, year_to, company):
            s["scope2_energy"] += self._calculate_emission_for_record(
                r.amount, r.unit, r.energy_type, country, year=r.year)

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

    def generate_trend_report(self, company: str, year_from: int, year_to: int) -> list[dict]:
        """Generuje raport trendów rok do roku dla spółki.
        Zwraca listę słowników z danymi emisji i % zmianą dla każdego roku."""
        trends = []
        prev = None
        for year in range(year_from, year_to + 1):
            s = self.generate_summary(year, year, company)
            scope1 = s["scope1_stationary"] + s["scope1_mobile"] + s["scope1_fugitive"] + s["scope1_process"]
            scope2 = s["scope2_energy"]
            total = s["total"]

            row = {
                "year": year, "company": company,
                "scope1_stationary": s["scope1_stationary"],
                "scope1_mobile": s["scope1_mobile"],
                "scope1_fugitive": s["scope1_fugitive"],
                "scope1_process": s["scope1_process"],
                "scope1_total": scope1,
                "scope2_energy": scope2,
                "total": total,
                "change_pct": None,
            }
            if prev is not None and prev > 0:
                change = ((total - prev) / prev * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                row["change_pct"] = change
            prev = total
            trends.append(row)
        return trends

    def display_trend_report(self, company: str, year_from: int, year_to: int):
        """Wyświetla raport trendów rok do roku w terminalu."""
        trends = self.generate_trend_report(company, year_from, year_to)
        if not trends:
            print("Brak danych do analizy trendów.")
            return

        print(f"\n{'═' * 80}")
        print(f" TRENDY ROK DO ROKU: {company}")
        print(f" Zakres: {year_from}–{year_to}")
        print(f"{'═' * 80}")
        print(f" {'Rok':<6} {'Scope 1':>12} {'Scope 2':>12} {'ŁĄCZNIE':>12} {'Zmiana %':>10}")
        print(f" {'─' * 6} {'─' * 12} {'─' * 12} {'─' * 12} {'─' * 10}")

        for t in trends:
            scope1 = t["scope1_total"]
            scope2 = t["scope2_energy"]
            total = t["total"]
            if t["change_pct"] is not None:
                pct = t["change_pct"]
                arrow = "↑" if pct > 0 else ("↓" if pct < 0 else "→")
                change_str = f"{arrow} {pct:+.1f}%"
            else:
                change_str = "—"
            print(f" {t['year']:<6} {scope1:>12.3f} {scope2:>12.3f} {total:>12.3f} {change_str:>10}")

        # Podsumowanie: zmiana pierwsza→ostatnia
        first_total = trends[0]["total"]
        last_total = trends[-1]["total"]
        if first_total > 0:
            overall = ((last_total - first_total) / first_total * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            print(f"{'─' * 80}")
            arrow = "↑" if overall > 0 else ("↓" if overall < 0 else "→")
            print(f" Zmiana {year_from}→{year_to}: {arrow} {overall:+.1f}%  ({first_total:.3f} → {last_total:.3f} tCO2e)")
        print(f"{'═' * 80}")
        return trends

    def display_trend_report_organization(self, login: str, year_from: int, year_to: int):
        """Wyświetla zbiorczy raport trendów dla całej organizacji."""
        companies = self.get_user_companies(login)
        if not companies:
            print("Brak przypisanych spółek.")
            return

        print(f"\n{'═' * 80}")
        print(f" TRENDY ROK DO ROKU — CAŁA ORGANIZACJA ({login})")
        print(f" Zakres: {year_from}–{year_to}")
        print(f"{'═' * 80}")

        # Sumujemy po latach
        yearly_totals = {}
        for year in range(year_from, year_to + 1):
            yearly_totals[year] = {"scope1": Decimal("0"), "scope2": Decimal("0"), "total": Decimal("0")}

        for company in companies:
            trends = self.generate_trend_report(company, year_from, year_to)
            for t in trends:
                yearly_totals[t["year"]]["scope1"] += t["scope1_total"]
                yearly_totals[t["year"]]["scope2"] += t["scope2_energy"]
                yearly_totals[t["year"]]["total"] += t["total"]

        print(f" {'Rok':<6} {'Scope 1':>12} {'Scope 2':>12} {'ŁĄCZNIE':>12} {'Zmiana %':>10}")
        print(f" {'─' * 6} {'─' * 12} {'─' * 12} {'─' * 12} {'─' * 10}")

        prev = None
        rows = []
        for year in range(year_from, year_to + 1):
            d = yearly_totals[year]
            total = d["total"]
            if prev is not None and prev > 0:
                pct = ((total - prev) / prev * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                arrow = "↑" if pct > 0 else ("↓" if pct < 0 else "→")
                change_str = f"{arrow} {pct:+.1f}%"
            else:
                change_str = "—"
            print(f" {year:<6} {d['scope1']:>12.3f} {d['scope2']:>12.3f} {total:>12.3f} {change_str:>10}")
            rows.append({"year": year, **d})
            prev = total

        first = yearly_totals[year_from]["total"]
        last = yearly_totals[year_to]["total"]
        if first > 0:
            overall = ((last - first) / first * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            print(f"{'─' * 80}")
            arrow = "↑" if overall > 0 else ("↓" if overall < 0 else "→")
            print(f" Zmiana {year_from}→{year_to}: {arrow} {overall:+.1f}%  ({first:.3f} → {last:.3f} tCO2e)")
        print(f"{'═' * 80}")
        return rows

    def export_summary_csv(self, summaries: list[dict], filename: str = "raport_emisji.csv") -> str:
        """Eksportuje podsumowanie emisji do pliku CSV w folderze export/."""
        import csv

        os.makedirs(EXPORT_FOLDER, exist_ok=True)
        filepath = os.path.join(EXPORT_FOLDER, filename)

        fieldnames = [
            "company", "years_label",
            "scope1_stationary", "scope1_mobile", "scope1_fugitive", "scope1_process",
            "scope2_energy", "total",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for s in summaries:
                writer.writerow({k: s.get(k, "") for k in fieldnames})

        print(f"  Wyeksportowano: {filepath}")
        return filepath

    def export_trend_csv(self, trends: list[dict], filename: str = "raport_trendy.csv") -> str:
        """Eksportuje raport trendów do pliku CSV w folderze export/."""
        import csv

        os.makedirs(EXPORT_FOLDER, exist_ok=True)
        filepath = os.path.join(EXPORT_FOLDER, filename)

        fieldnames = [
            "year", "company",
            "scope1_stationary", "scope1_mobile", "scope1_fugitive", "scope1_process",
            "scope1_total", "scope2_energy", "total", "change_pct",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for t in trends:
                row = {k: t.get(k, "") for k in fieldnames}
                if row["change_pct"] is None:
                    row["change_pct"] = ""
                writer.writerow(row)

        print(f"  Wyeksportowano: {filepath}")
        return filepath

    def validate_data_consistency(self) -> list[str]:
        """Sprawdza spójność danych:
        1. Czy firmy w tabelach emisyjnych istnieją w tbl_companies
        2. Czy w spalaniu stacjonarnym raport=TRUE ale emission=0 (brak podanej emisji)"""
        issues = []
        companies, _ = self.repos.companies.get_all()
        valid_names = {c.co_name for c in companies}

        emission_repos = [
            ("spalanie stacjonarne", self.repos.stationary),
            ("spalanie mobilne", self.repos.mobile),
            ("emisje procesowe", self.repos.process),
            ("emisje niezorganizowane", self.repos.fugitive),
            ("zużycie energii", self.repos.energy_consumption),
        ]

        for table_name, repo in emission_repos:
            records, _ = repo.get_all()
            for r in records:
                if r.company not in valid_names:
                    issues.append(
                        f"[{table_name}] ID {r.id}: firma '{r.company}' nie istnieje w tbl_companies.csv"
                    )

        # Sprawdź spójność emission_tco2eq i raport we wszystkich tabelach emisyjnych
        emission_tables = [
            ("spalanie stacjonarne", self.repos.stationary),
            ("spalanie mobilne", self.repos.mobile),
            ("emisje procesowe", self.repos.process),
            ("emisje niezorganizowane", self.repos.fugitive),
        ]
        for table_name, repo in emission_tables:
            records, _ = repo.get_all()
            for r in records:
                # emission_tco2eq wypełnione ale raport pusty
                if r.emission_tco2eq is not None and r.emission_tco2eq > 0 and not r.raport:
                    issues.append(
                        f"[{table_name}] ID {r.id}: emission_tco2eq={r.emission_tco2eq} ale brak pola raport "
                        f"({r.company}, {r.amount} {r.unit})"
                    )
                # raport wypełniony ale emission_tco2eq puste
                if r.raport and (r.emission_tco2eq is None or r.emission_tco2eq == 0):
                    issues.append(
                        f"[{table_name}] ID {r.id}: raport='{r.raport}' ale emission_tco2eq puste "
                        f"({r.company}, {r.amount} {r.unit})"
                    )

        # Sprawdź autoryzacje
        auth_records, _ = self.repos.authorisations.get_all()
        for r in auth_records:
            if r.company not in valid_names:
                issues.append(
                    f"[autoryzacje] ID {r.id}: firma '{r.company}' nie istnieje w tbl_companies.csv"
                )

        return issues

    def display_data_consistency_report(self):
        """Wyświetla raport spójności danych w terminalu."""
        print(f"\n─── Walidacja spójności danych ───\n")
        issues = self.validate_data_consistency()
        if not issues:
            print("  Wszystkie dane spójne — firmy w tabelach emisyjnych istnieją w rejestrze firm. ✓")
            return
        for issue in issues:
            print(f"  ✗ {issue}")
        print(f"\n  Łącznie problemów: {len(issues)}")

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
                factor_obj = self.repos.factors.get_factor(
                    factor_key_value, country, year=record.year
                )

                if not factor_obj:
                    issues.append({
                        "tabela_zrodlowa": source_name,
                        "id": record.id,
                        "info": f"Brak wskaźnika emisji dla: '{factor_key_value}' (kraj: {country}, rok: {record.year})",
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

    # ── Cele redukcji i symulacje ────────────────────────────────────

    def add_reduction_target_interactive(self, allowed_companies: Optional[list[str]] = None) -> bool:
        """Interaktywne dodawanie celu redukcji emisji."""
        print("\n─── Dodawanie: Cel redukcji emisji ───")
        print("(Wpisz 'q' aby anulować)\n")

        if allowed_companies:
            company = self._choose_company_from_list(allowed_companies)
        else:
            company = safe_input("Firma: ")
        if company is None: return False

        target_name = safe_input("Nazwa celu (np. 'SBTi 1.5C', 'Strategia 2030'): ")
        if target_name is None: return False

        base_year = safe_int("Rok bazowy: ", MIN_YEAR, MAX_YEAR)
        if base_year is None: return False

        target_year = safe_int("Rok docelowy: ", base_year + 1, 2100)
        if target_year is None: return False

        reduction_pct = safe_decimal("Cel redukcji w % (np. 42 = spadek o 42%): ",
                                      min_val=Decimal("0.1"), max_val=Decimal("100"))
        if reduction_pct is None: return False

        scope = safe_choice("Zakres: ", ["1", "2", "1+2"])
        if scope is None: return False

        notes = safe_input("Uwagi (opcjonalne): ", allow_empty=True) or None

        # Pokaż ścieżkę redukcji
        years = target_year - base_year
        annual_rate = (reduction_pct / years).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        print(f"\n  Cel: redukcja o {reduction_pct}% w {years} lat ({base_year}→{target_year})")
        print(f"  Wymagana roczna redukcja: ~{annual_rate}%/rok (ścieżka liniowa)")

        if not confirm("\nZapisać cel? "):
            print("Anulowano.")
            return False

        record = ReductionTarget(
            id=self.repos.reduction_targets.next_id(),
            company=company, target_name=target_name,
            base_year=base_year, target_year=target_year,
            reduction_pct=reduction_pct, scope=scope, notes=notes,
        )
        ok, msg = self.repos.reduction_targets.add(record)
        print(f"{'Zapisano cel!' if ok else f'Błąd: {msg}'}")
        return ok

    def get_reduction_path(self, target: ReductionTarget, base_emission: Decimal) -> list[dict]:
        """Oblicza ścieżkę redukcji liniowej od roku bazowego do docelowego.

        Zwraca listę dict z kluczami: year, target_emission, reduction_pct_cumulative.
        """
        R = lambda d: d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        years = target.target_year - target.base_year
        annual_reduction = base_emission * target.reduction_pct / 100 / years
        path = []

        for i in range(years + 1):
            year = target.base_year + i
            target_emission = R(base_emission - annual_reduction * i)
            if target_emission < 0:
                target_emission = Decimal("0")
            cumulative_pct = R(Decimal(i) * target.reduction_pct / years)
            path.append({
                "year": year,
                "target_emission": target_emission,
                "reduction_pct_cumulative": cumulative_pct,
            })
        return path

    def display_reduction_progress(self, company: str):
        """Wyświetla postęp redukcji emisji vs cele."""
        targets = self.repos.reduction_targets.get_for_company(company)
        if not targets:
            print(f"\n  Brak celów redukcji dla: {company}")
            print("  Dodaj cel w menu: Cele i symulacje → Dodaj cel redukcji")
            return

        for target in targets:
            # Emisja w roku bazowym
            base_summary = self.generate_summary(target.base_year, target.base_year, company)
            if target.scope == "1":
                base_emission = (base_summary["scope1_stationary"] + base_summary["scope1_mobile"] +
                                 base_summary["scope1_fugitive"] + base_summary["scope1_process"])
            elif target.scope == "2":
                base_emission = base_summary["scope2_energy"]
            else:
                base_emission = base_summary["total"]

            if base_emission <= 0:
                print(f"\n  [{target.target_name}] Brak danych za rok bazowy {target.base_year}.")
                continue

            path = self.get_reduction_path(target, base_emission)
            current_year = MAX_YEAR  # bieżący rok

            print(f"\n{'═' * 70}")
            print(f"  CEL: {target.target_name} ({company})")
            print(f"  Zakres: Scope {target.scope} | {target.base_year}→{target.target_year} | -{target.reduction_pct}%")
            print(f"  Emisja bazowa ({target.base_year}): {base_emission:.3f} tCO2e")
            print(f"{'═' * 70}")
            print(f"  {'Rok':<6} {'Cel [tCO2e]':>14} {'Rzeczywista':>14} {'Status':>14} {'Odchylenie':>12}")
            print(f"  {'─'*6} {'─'*14} {'─'*14} {'─'*14} {'─'*12}")

            for point in path:
                year = point["year"]
                target_em = point["target_emission"]

                if year > current_year:
                    # Rok w przyszłości — brak danych
                    print(f"  {year:<6} {target_em:>14.3f} {'—':>14} {'(przyszłość)':>14} {'—':>12}")
                    continue

                # Rzeczywista emisja
                actual_summary = self.generate_summary(year, year, company)
                if target.scope == "1":
                    actual = (actual_summary["scope1_stationary"] + actual_summary["scope1_mobile"] +
                              actual_summary["scope1_fugitive"] + actual_summary["scope1_process"])
                elif target.scope == "2":
                    actual = actual_summary["scope2_energy"]
                else:
                    actual = actual_summary["total"]

                if actual <= 0 and year != target.base_year:
                    print(f"  {year:<6} {target_em:>14.3f} {'brak danych':>14} {'—':>14} {'—':>12}")
                    continue

                diff = actual - target_em
                if target_em > 0:
                    diff_pct = (diff / target_em * 100).quantize(Decimal("0.1"))
                else:
                    diff_pct = Decimal("0")

                if actual <= target_em:
                    status = "✓ na torze"
                else:
                    status = "✗ powyżej"

                print(f"  {year:<6} {target_em:>14.3f} {actual:>14.3f} {status:>14} {diff_pct:>+11.1f}%")

            # Podsumowanie
            target_final = path[-1]["target_emission"]
            print(f"  {'─'*60}")
            print(f"  Cel końcowy ({target.target_year}): {target_final:.3f} tCO2e "
                  f"(redukcja o {target.reduction_pct}% vs {target.base_year})")
            print(f"{'═' * 70}")

    def simulate_what_if(self, company: str, year: int,
                         scenarios: list[dict]) -> dict:
        """Symulacja what-if — co jeśli zmienimy źródła energii/paliwa?

        Args:
            company: firma
            year: rok do symulacji
            scenarios: lista scenariuszy, każdy to dict:
                - strategy: "fuel_switch" | "oze_switch" | "efficiency" | "custom"
                - params: parametry zależne od strategii

        Strategie:
            fuel_switch: {"from_fuel": "węgiel", "to_fuel": "gaz ziemny"}
                → przelicza ilość paliwa na nowe i oblicza nową emisję
            oze_switch: {"pct": 50}
                → % energii nie-OZE zamienione na OZE (emisja Scope 2 = 0)
            efficiency: {"pct": 10}
                → zmniejszenie zużycia o X% (wpływa na Scope 1 + 2)
            custom: {"scope1_reduction_pct": 20, "scope2_reduction_pct": 30}
                → bezpośrednia redukcja procentowa

        Returns:
            dict z kluczami: baseline (dict summary), simulated (dict summary),
            savings (Decimal), savings_pct (Decimal)
        """
        R = lambda d: d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        baseline = self.generate_summary(year, year, company)
        sim = dict(baseline)  # kopia

        for scenario in scenarios:
            strategy = scenario.get("strategy", "")
            params = scenario.get("params", {})

            if strategy == "oze_switch":
                # Zamień X% energii nie-OZE na OZE → Scope 2 spada
                pct = Decimal(str(params.get("pct", 0))) / 100
                sim["scope2_energy"] = R(sim["scope2_energy"] * (1 - pct))

            elif strategy == "efficiency":
                # Redukcja zużycia o X% → wpływa na wszystkie scope
                pct = Decimal(str(params.get("pct", 0))) / 100
                factor = 1 - pct
                for key in ("scope1_stationary", "scope1_mobile", "scope1_fugitive",
                            "scope1_process", "scope2_energy"):
                    sim[key] = R(sim[key] * factor)

            elif strategy == "fuel_switch":
                # Zamiana paliwa — przelicz emisję stacjonarną (wskaźnik z roku symulacji)
                from_fuel = params.get("from_fuel", "")
                to_fuel = params.get("to_fuel", "")
                if from_fuel and to_fuel:
                    factor_from = self.repos.factors.get_factor(from_fuel, "Polska", year=year)
                    factor_to = self.repos.factors.get_factor(to_fuel, "Polska", year=year)
                    if factor_from and factor_to and factor_from.factor > 0:
                        ratio = factor_to.factor / factor_from.factor
                        sim["scope1_stationary"] = R(sim["scope1_stationary"] * ratio)

            elif strategy == "custom":
                s1_pct = Decimal(str(params.get("scope1_reduction_pct", 0))) / 100
                s2_pct = Decimal(str(params.get("scope2_reduction_pct", 0))) / 100
                for key in ("scope1_stationary", "scope1_mobile", "scope1_fugitive", "scope1_process"):
                    sim[key] = R(sim[key] * (1 - s1_pct))
                sim["scope2_energy"] = R(sim["scope2_energy"] * (1 - s2_pct))

        # Przelicz total
        sim["total"] = sum(v for k, v in sim.items() if k.startswith("scope") and isinstance(v, Decimal))
        savings = R(baseline["total"] - sim["total"])
        savings_pct = R(savings / baseline["total"] * 100) if baseline["total"] > 0 else Decimal("0")

        return {
            "baseline": baseline,
            "simulated": sim,
            "savings": savings,
            "savings_pct": savings_pct,
        }

    def display_simulation_result(self, result: dict):
        """Wyświetla wynik symulacji what-if w terminalu."""
        b = result["baseline"]
        s = result["simulated"]

        print(f"\n{'═' * 65}")
        print(f"  SYMULACJA WHAT-IF: {b['company']} ({b['years_label']})")
        print(f"{'═' * 65}")
        print(f"  {'Kategoria':<30} {'Obecna':>14} {'Symulacja':>14}")
        print(f"  {'─'*30} {'─'*14} {'─'*14}")

        categories = [
            ("Scope 1 — stacjonarne", "scope1_stationary"),
            ("Scope 1 — mobilne", "scope1_mobile"),
            ("Scope 1 — niezorganizowane", "scope1_fugitive"),
            ("Scope 1 — procesowe", "scope1_process"),
            ("Scope 2 — energia", "scope2_energy"),
        ]
        for label, key in categories:
            print(f"  {label:<30} {b[key]:>14.3f} {s[key]:>14.3f}")

        print(f"  {'─'*30} {'─'*14} {'─'*14}")
        print(f"  {'ŁĄCZNIE':<30} {b['total']:>14.3f} {s['total']:>14.3f}")
        print(f"{'═' * 65}")
        print(f"  Oszczędność: {result['savings']:.3f} tCO2e ({result['savings_pct']:.1f}%)")
        print(f"{'═' * 65}")


    def get_repo_by_table_name(self, table_name: str):
        """Zwraca repozytorium po nazwie tabeli."""
        repo_map = {
            "stationary": self.repos.stationary,
            "mobile": self.repos.mobile,
            "process": self.repos.process,
            "fugitive": self.repos.fugitive,
            "energy_consumption": self.repos.energy_consumption,
            "energy_purchased": self.repos.energy_purchased,
        }
        return repo_map.get(table_name)

    def check_record_access(self, record_id: int, table_name: str, login: str) -> tuple[bool, str]:
        """Sprawdza czy użytkownik ma uprawnienia do rekordu (read na spółce rekordu).

        Zwraca (czy_ma_dostep, nazwa_spolki_lub_komunikat_bledu).
        """
        repo = self.get_repo_by_table_name(table_name)
        if not repo:
            return False, f"Nieznana tabela: {table_name}"
        record = repo.get_by_id(record_id)
        if not record:
            return False, f"Nie znaleziono rekordu o ID {record_id} w tabeli {table_name}"
        user_companies = self.get_user_companies(login, read_only=True)
        if record.company not in user_companies:
            return False, f"Brak uprawnień do spółki: {record.company} (rekord #{record_id})"
        return True, record.company

    def log_sent_email(self, sender: str, recipients: list[str], company: str,
                       template_type: str, subject: str,
                       table_name: Optional[str] = None,
                       record_ids: Optional[list[int]] = None,
                       scope: Optional[str] = None,
                       year: Optional[int] = None):
        """Zapisuje informację o wysłanym mailu do tbl_email_log.csv."""
        from app.application.class_models import EmailLog
        from datetime import datetime

        log_entry = EmailLog(
            id=self.repos.email_log.next_id(),
            date=datetime.now(),
            sender=sender,
            recipients="; ".join(recipients),
            company=company,
            table_name=table_name,
            record_ids=",".join(str(i) for i in record_ids) if record_ids else None,
            template_type=template_type,
            subject=subject,
            scope=scope,
            year=year,
        )
        self.repos.email_log.add(log_entry)