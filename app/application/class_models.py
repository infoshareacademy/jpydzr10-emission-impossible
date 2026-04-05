from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

MIN_YEAR = 2010
MAX_YEAR = datetime.now().year  # nie pozwalamy wpisać roku w przyszłości

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")

ENERGY_UNITS = {"MWh", "kWh", "GJ", "MJ"}
MASS_UNITS = {"kg", "t", "Mg"}
VOLUME_UNITS = {"l", "m3"}
ALL_UNITS = ENERGY_UNITS | MASS_UNITS | VOLUME_UNITS

FUEL_TYPES = {
    "gaz ziemny",
    "olej opałowy lekki",
    "olej opałowy ciężki",
    "węgiel kamienny",
    "benzyna",
    "diesel",
    "LPG",
    "biomasa",
}

DATA_QUALITY_LEVELS = {"measured", "calculated", "estimated"}


class BaseRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    id: int = Field(ge=0, description="Unikalny ID wiersza")
    year: int = Field(ge=MIN_YEAR, le=MAX_YEAR, description="Rok sprawozdawczy")
    company: str = Field(min_length=1, max_length=200, description="Nazwa firmy")
    data_quality: Optional[str] = Field(
        default=None, max_length=20,
        description="Poziom pewności danych: measured / calculated / estimated"
    )

    @field_validator("data_quality", mode="before")
    @classmethod
    def parse_data_quality(cls, v) -> Optional[str]:
        """Parsuje i normalizuje poziom pewności danych."""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        v = v.strip().lower()
        if v not in DATA_QUALITY_LEVELS:
            raise ValueError(
                f"Nieznany poziom pewności '{v}'. Dozwolone: {sorted(DATA_QUALITY_LEVELS)}"
            )
        return v

    @field_validator("company")
    @classmethod
    def company_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nazwa firmy nie może być pusta")
        return v.strip()


class ActivityRecord(BaseRecord):
    amount: Decimal = Field(ge=0, description="Ilość — musi być >= 0")
    unit: str = Field(min_length=1, max_length=20)
    source: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Źródło danych (faktura, szacunek itp.)"
    )

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        v = v.strip()
        if v not in ALL_UNITS:
            raise ValueError(
                f"Nieznana jednostka '{v}'. Dozwolone: {sorted(ALL_UNITS)}"
            )
        return v


class StationaryCombustion(ActivityRecord):
    fuel: str = Field(min_length=1, max_length=100, description="Rodzaj paliwa")
    installation: str = Field(min_length=1, max_length=200, description="Nazwa instalacji")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja deklarowana [tCO2eq]")
    raport: Optional[str] = Field(default=None, max_length=300, description="Źródło raportu emisji")
    notes: Optional[str] = Field(default=None, max_length=500, description="Uwagi do rekordu")

    @field_validator("emission_tco2eq", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Optional[Decimal]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("fuel")
    @classmethod
    def validate_fuel(cls, v: str) -> str:
        v = v.strip()
        if v not in FUEL_TYPES:
            raise ValueError(
                f"Nieznany typ paliwa '{v}'. Dozwolone: {sorted(FUEL_TYPES)}"
            )
        return v

    @field_validator("raport", mode="before")
    @classmethod
    def parse_raport(cls, v) -> Optional[str]:
        """Parsuje pole raport — obsługuje stare wartości TRUE/FALSE i nowe stringi."""
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        if isinstance(v, bool):
            return None  # Stary format — ignoruj
        return v.strip()


class MobileCombustion(ActivityRecord):
    vehicle: str = Field(min_length=1, max_length=200, description="Typ pojazdu")
    fuel: str = Field(min_length=1, max_length=100, description="Rodzaj paliwa")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja deklarowana [tCO2eq]")
    raport: Optional[str] = Field(default=None, max_length=300, description="Źródło raportu emisji")
    notes: Optional[str] = Field(default=None, max_length=500, description="Uwagi do rekordu")

    @field_validator("emission_tco2eq", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Optional[Decimal]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("fuel")
    @classmethod
    def validate_fuel(cls, v: str) -> str:
        v = v.strip()
        if v not in FUEL_TYPES:
            raise ValueError(
                f"Nieznany typ paliwa '{v}'. Dozwolone: {sorted(FUEL_TYPES)}"
            )
        return v

    @field_validator("raport", mode="before")
    @classmethod
    def parse_raport(cls, v) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else None


class ProcessEmission(ActivityRecord):
    process: str = Field(min_length=1, max_length=200, description="Nazwa procesu")
    product: str = Field(min_length=1, max_length=200, description="Produkt")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja deklarowana [tCO2eq]")
    raport: Optional[str] = Field(default=None, max_length=300, description="Źródło raportu emisji")
    notes: Optional[str] = Field(default=None, max_length=500, description="Uwagi do rekordu")

    @field_validator("emission_tco2eq", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Optional[Decimal]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("raport", mode="before")
    @classmethod
    def parse_raport(cls, v) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else None


class FugitiveEmission(ActivityRecord):
    installation: str = Field(min_length=1, max_length=200, description="Nazwa instalacji")
    product: str = Field(min_length=1, max_length=200, description="Czynnik chłodniczy")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja deklarowana [tCO2eq]")
    raport: Optional[str] = Field(default=None, max_length=300, description="Źródło raportu emisji")
    notes: Optional[str] = Field(default=None, max_length=500, description="Uwagi do rekordu")

    @field_validator("emission_tco2eq", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Optional[Decimal]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("raport", mode="before")
    @classmethod
    def parse_raport(cls, v) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else None


class EmissionFactor(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0)
    factor_name: str = Field(min_length=1, max_length=200, description="Nazwa wskaźnika")
    country: str = Field(min_length=1, max_length=100, description="Kraj")
    factor: Decimal = Field(ge=0, description="Wartość wskaźnika")
    unit_factor: str = Field(min_length=1, max_length=50, description="Jednostka")
    source: Optional[str] = Field(default=None, max_length=200, description="Źródło wskaźnika")


class UnitConverter(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0)
    unit_from: str = Field(min_length=1, max_length=20, description="Jednostka konwertowana")
    unit_to: str = Field(min_length=1, max_length=20, description="Jednostka przekonwertowana")
    factor: Decimal = Field(gt=0, description="Mnożnik konwersji — musi być > 0")


class Company(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    co_id: int = Field(ge=0)
    co_name: str = Field(min_length=1, max_length=200)
    co_country: str = Field(min_length=1, max_length=100)
    co_city: str = Field(min_length=1, max_length=100)
    co_street: str = Field(min_length=1, max_length=200)
    co_zip: str = Field(min_length=1, max_length=20)
    co_tel: str = Field(min_length=1, max_length=30)
    co_mail: str = Field(min_length=1, max_length=200)
    co_krs: str = Field(max_length=20)
    co_regon: str = Field(max_length=20)
    co_nip: str = Field(max_length=20)
    cg_name: str = Field(min_length=1, max_length=200, description="Grupa kapitałowa")

    @field_validator("co_mail")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip()
        if not EMAIL_REGEX.match(v):
            raise ValueError(f"Nieprawidłowy email: '{v}'")
        return v

    @field_validator("co_tel")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not PHONE_REGEX.match(v):
            raise ValueError(f"Nieprawidłowy telefon: '{v}'")
        return v

    @field_validator("co_nip")
    @classmethod
    def validate_nip(cls, v: str) -> str:
        digits = re.sub(r"[\s\-]", "", v.strip())
        if not digits.isdigit() or len(digits) != 10:
            raise ValueError(f"NIP musi mieć 10 cyfr, podano: '{v}'")
        return v.strip()

    @field_validator("co_regon")
    @classmethod
    def validate_regon(cls, v: str) -> str:
        digits = re.sub(r"[\s\-]", "", v.strip())
        if not digits.isdigit() or len(digits) not in (9, 14):
            raise ValueError(f"REGON musi mieć 9 lub 14 cyfr, podano: '{v}'")
        return v.strip()

    @field_validator("co_krs")
    @classmethod
    def validate_krs(cls, v: str) -> str:
        digits = re.sub(r"[\s\-]", "", v.strip())
        if not digits.isdigit() or len(digits) != 10:
            raise ValueError(f"KRS musi mieć 10 cyfr, podano: '{v}'")
        return v.strip()


class UserAuthorization(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0, description="Unikalny ID")
    login: str = Field(min_length=1, max_length=100)
    company: str = Field(min_length=1, max_length=200)
    save: bool = Field(default=False)
    read: bool = Field(default=False)

    @field_validator("save", "read", mode="before")
    @classmethod
    def parse_bool(cls, v) -> bool:
        if isinstance(v, str):
            return v.strip().upper() in ("TRUE", "1", "TAK", "YES", "T")
        return bool(v)


# Dozwolone role użytkowników
USER_ROLES = {"admin", "użytkownik"}


class UserPermission(BaseModel):
    """Model dla tbl_permissions.csv — rola użytkownika w systemie."""
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0, description="Unikalny ID")
    login: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=50, description="Rola: admin lub użytkownik")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in USER_ROLES:
            raise ValueError(f"Nieznana rola '{v}'. Dozwolone: {sorted(USER_ROLES)}")
        return v

ENERGY_SOURCE_TYPES = {
    "Zakupiona",
    "Wyprodukowana",
    "Sprzedana",
    "Zużyta",
}

ENERGY_TYPES = {
    "Energia elektryczna z OZE",
    "Energia elektryczna nie OZE",
    "Ciepło z OZE",
    "Ciepło nie OZE",
    "Chłód z OZE",
    "Chłód nie OZE",
    "Para Techniczna z OZE",
    "Para Techniczna nie OZE",
}

# Model dla tbl_e_cons.csv — zużycie energii (Scope 2)
# Dziedziczy z ActivityRecord, więc ma już pola: id, year, company, amount, unit, source
class EnergyConsumption(ActivityRecord):
    """Model dla tbl_e_cons.csv — zużycie energii (Scope 2)"""
    energy_source: str = Field(min_length=1, max_length=100, description="Źródło energii")
    energy_type: str = Field(min_length=1, max_length=100, description="Typ energii")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja CO2e [tCO2eq]")

    @field_validator("emission_tco2eq", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Optional[Decimal]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

# Model dla tbl_e_purc.csv — zakupiona energia (Scope 2)
# Rozszerza ActivityRecord o dane dostawcy i wskaźnik emisji
class EnergyPurchased(ActivityRecord):
    """Model dla tbl_e_purc.csv — zakupiona energia (Scope 2)"""
    energy_type: str = Field(min_length=1, max_length=100, description="Typ energii")
    trader: str = Field(default="", max_length=200, description="Dostawca energii")
    factor: Decimal = Field(default=Decimal("0"), ge=0, description="Wskaźnik emisji")
    emission_tco2eq: Optional[Decimal] = Field(default=None, ge=0, description="Emisja CO2e [tCO2eq]")

    @field_validator("emission_tco2eq", "factor", mode="before")
    @classmethod
    def parse_decimal(cls, v):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

REDUCTION_STRATEGIES = {"fuel_switch", "oze_switch", "efficiency", "custom"}


class ReductionTarget(BaseModel):
    """Model dla tbl_reduction_targets.csv — cele redukcji emisji (SBTi-style).

    Przechowuje cele redukcyjne: rok bazowy, rok docelowy, cel procentowy.
    Ścieżka redukcji liniowa: stała redukcja % rocznie od base_year do target_year.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0, description="Unikalny ID celu")
    company: str = Field(min_length=1, max_length=200, description="Nazwa firmy")
    target_name: str = Field(min_length=1, max_length=300, description="Nazwa celu (np. 'SBTi 1.5C')")
    base_year: int = Field(ge=MIN_YEAR, le=MAX_YEAR, description="Rok bazowy")
    target_year: int = Field(ge=MIN_YEAR, description="Rok docelowy")
    reduction_pct: Decimal = Field(gt=0, le=100, description="Cel redukcji w % (np. 42 = -42%)")
    scope: str = Field(default="1+2", max_length=10, description="Zakres: 1, 2, 1+2")
    notes: Optional[str] = Field(default=None, max_length=500, description="Uwagi")

    @field_validator("target_year")
    @classmethod
    def target_after_base(cls, v, info):
        base = info.data.get("base_year")
        if base is not None and v <= base:
            raise ValueError(f"Rok docelowy ({v}) musi być późniejszy niż bazowy ({base})")
        return v

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        v = v.strip()
        if v not in ("1", "2", "1+2"):
            raise ValueError(f"Nieprawidłowy zakres '{v}'. Dozwolone: 1, 2, 1+2")
        return v

    @field_validator("reduction_pct", mode="before")
    @classmethod
    def parse_reduction(cls, v):
        if isinstance(v, str) and v.strip():
            return Decimal(v.strip())
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def parse_notes(cls, v) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else None


EMAIL_TEMPLATE_TYPES = {
    "weryfikacja",      # potwierdzenie poprawności danych
    "korekta",          # prośba o korektę danych
    "brak_danych",      # brakujące dane w porównaniu do roku ubiegłego
    "odchylenie",       # wyjaśnienie wzrostu/spadku emisji
    "wlasna",           # dowolna treść
    "dane_zrodlowe",    # prośba o dokumenty potwierdzające
}


class EmailLog(BaseModel):
    """Model dla tbl_email_log.csv — rejestr wysłanych wiadomości.

    Każdy wysłany mail jest logowany tutaj — historia komunikacji z osobami
    odpowiedzialnymi za dane emisyjne.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(ge=0, description="Unikalny ID wiadomości")
    date: datetime = Field(description="Data wysłania (YYYY-MM-DD HH:MM:SS)")
    sender: str = Field(min_length=1, max_length=100, description="Login nadawcy")
    recipients: str = Field(min_length=1, max_length=1000, description="Adresy e-mail odbiorców (rozdzielone ;)")
    company: str = Field(min_length=1, max_length=200, description="Nazwa spółki której dotyczy")
    table_name: Optional[str] = Field(default=None, max_length=200, description="Tabela (jeśli dotyczy konkretnej)")
    record_ids: Optional[str] = Field(default=None, max_length=500, description="ID rekordów (rozdzielone ,)")
    template_type: str = Field(min_length=1, max_length=50, description="Typ szablonu wiadomości")
    subject: str = Field(min_length=1, max_length=500, description="Temat wiadomości")
    scope: Optional[str] = Field(default=None, max_length=10, description="Zakres: 1, 2, 1+2 (jeśli dotyczy)")
    year: Optional[int] = Field(default=None, ge=MIN_YEAR, description="Rok którego dotyczy zapytanie")

    @field_validator("template_type")
    @classmethod
    def validate_template_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in EMAIL_TEMPLATE_TYPES:
            raise ValueError(f"Nieznany typ szablonu '{v}'. Dozwolone: {sorted(EMAIL_TEMPLATE_TYPES)}")
        return v

    @field_validator("date", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime:
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            v = v.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Nie można sparsować daty: '{v}'")
        return v

    @field_validator("record_ids", "table_name", "scope", mode="before")
    @classmethod
    def parse_optional_str(cls, v) -> Optional[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return None
        return v.strip() if isinstance(v, str) else None


CHANGE_TYPES = {"INSERT", "UPDATE", "DELETE"}

class ChangeLog(BaseModel):
    """Model dla tbl_change_log.csv — rejestr zmian (audit log).

    Działa jak trigger SQL — rejestruje każdą zmianę w dowolnej tabeli.
    Pola previous_data i actual_data przechowują JSON (docelowo JSONB w SQL).
    Rekord jest niezmienny — tylko INSERT, nigdy UPDATE ani DELETE na tym logu.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    id_rejestr_zmian: int = Field(ge=1, description="Klucz serial — auto-generowany")
    login: str = Field(min_length=1, max_length=100, description="Login użytkownika który wykonał zmianę")
    date_change: datetime = Field(description="Data i godzina zmiany (YYYY-MM-DD HH:MM:SS)")
    table_name: str = Field(min_length=1, max_length=200, description="Nazwa tabeli (pliku CSV) w której nastąpiła zmiana")
    record_id: str = Field(max_length=50, description="ID zmienionego rekordu")
    change_type: str = Field(min_length=1, max_length=10, description="Typ zmiany: INSERT, UPDATE lub DELETE")
    previous_data: Optional[str] = Field(default=None, description="JSON z danymi przed zmianą (null przy INSERT)")
    actual_data: Optional[str] = Field(default=None, description="JSON z danymi po zmianie (null przy DELETE)")

    @field_validator("change_type")
    @classmethod
    def validate_change_type(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in CHANGE_TYPES:
            raise ValueError(f"Nieznany typ zmiany '{v}'. Dozwolone: {sorted(CHANGE_TYPES)}")
        return v

    @field_validator("date_change", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime:
        """Parsuje datetime z różnych formatów — CSV przechowuje string."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            v = v.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Nie można sparsować daty: '{v}'")
        return v
