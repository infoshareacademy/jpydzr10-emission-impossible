from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

MIN_YEAR = 2010
MAX_YEAR = 2030

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
PHONE_REGEX = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")

# Tu można dodać pliki csv słownikowe
ENERGY_UNITS = {"MWh", "kWh", "GJ", "MJ"}
MASS_UNITS = {"kg", "t", "Mg"}
VOLUME_UNITS = {"l", "m3"}
ALL_UNITS = ENERGY_UNITS | MASS_UNITS | VOLUME_UNITS

# Tu można dodać pliki csv słownikowe
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

class BaseRecord(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )
    id: int = Field(ge=0, description="Unikalny ID wiersza")
    year: int = Field(ge=MIN_YEAR, le=MAX_YEAR, description="Rok sprawozdawczy")
    company: str = Field(min_length=1, max_length=200, description="Nazwa firmy")

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
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja")
    raport: bool = Field(default=False, description="Czy dane z raportu")

    @field_validator("emission", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
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
    def parse_bool(cls, v) -> bool:
        if isinstance(v, str):
            return v.strip().upper() in ("TRUE", "1", "TAK", "YES", "T")
        return bool(v)


class MobileCombustion(ActivityRecord):
    vehicle: str = Field(min_length=1, max_length=200, description="Typ pojazdu")
    fuel: str = Field(min_length=1, max_length=100, description="Rodzaj paliwa")
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja")

    @field_validator("emission", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
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


class ProcessEmission(ActivityRecord):
    process: str = Field(min_length=1, max_length=200, description="Nazwa procesu")
    product: str = Field(min_length=1, max_length=200, description="Produkt")
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja")

    @field_validator("emission", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
        return v


class FugitiveEmission(ActivityRecord):
    installation: str = Field(min_length=1, max_length=200, description="Nazwa instalacji")
    product: str = Field(min_length=1, max_length=200, description="Czynnik chłodniczy")
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja")

    @field_validator("emission", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
        return v


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

# Dozwolone źródła energii — używane przy walidacji danych wejściowych
ENERGY_SOURCE_TYPES = {
    "Zakupiona",
    "Wyprodukowana",
    "Sprzedana",
    "Zużyta",
}

# Dozwolone typy energii — muszą odpowiadać nazwom w tbl_factors.csv
ENERGY_TYPES = {
    "Energia elektryczna",
    "Energia elektryczna z OZE",
    "Energia elektryczna nie OZE",
    "Ciepło",
    "Chłód",
}

# Model dla tbl_e_cons.csv — zużycie energii (Scope 2)
# Dziedziczy z ActivityRecord, więc ma już pola: id, year, company, amount, unit, source
class EnergyConsumption(ActivityRecord):
    """Model dla tbl_e_cons.csv — zużycie energii (Scope 2)"""
    energy_source: str = Field(min_length=1, max_length=100, description="Źródło energii")
    energy_type: str = Field(min_length=1, max_length=100, description="Typ energii")
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja CO2e")

    @field_validator("emission", mode="before")
    @classmethod
    def parse_emission(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
        return v

# Model dla tbl_e_purc.csv — zakupiona energia (Scope 2)
# Rozszerza ActivityRecord o dane dostawcy i wskaźnik emisji
class EnergyPurchased(ActivityRecord):
    """Model dla tbl_e_purc.csv — zakupiona energia (Scope 2)"""
    energy_type: str = Field(min_length=1, max_length=100, description="Typ energii")
    trader: str = Field(default="", max_length=200, description="Dostawca energii")
    factor: Decimal = Field(default=Decimal("0"), ge=0, description="Wskaźnik emisji")
    emission: Decimal = Field(default=Decimal("0"), ge=0, description="Emisja CO2e")

    @field_validator("emission", "factor", mode="before")
    @classmethod
    def parse_decimal(cls, v) -> Decimal:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return Decimal("0")
        return v

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
