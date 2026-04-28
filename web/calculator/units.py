"""
units.py — Rejestr jednostek dla kalkulatora emisji CO2.

Używa biblioteki pint do obsługi konwersji jednostek.
Definiuje jednostki specyficzne dla projektu (CO2e, m3, Mg).

Użycie:
    from calculator.units import ureg, Q_, convert, parse_factor_unit
"""

import pint
from dataclasses import dataclass
from typing import Optional

# ── Rejestr jednostek ────────────────────────────────────────────────────────

ureg = pint.UnitRegistry()
ureg.formatter.default_format = "~P"
ureg.define("tCO2e  = 1 * metric_ton")
ureg.define("kgCO2e = 1 * kilogram")
ureg.define("m3 = 1 * meter ** 3")
ureg.define("Mg = 1 * metric_ton")

Q_ = ureg.Quantity

_UNIT_ALIASES: dict[str, str] = {
    # energia
    "MWh": "MWh",
    "kWh": "kWh",
    "GJ":  "GJ",
    "MJ":  "MJ",
    # masa
    "kg":  "kg",
    "t":   "metric_ton",
    "Mg":  "Mg",
    # objętość
    "l":   "liter",
    "m3":  "m3",
    # CO2 (wynik wskaźnika)
    "tCO2e":  "tCO2e",
    "kgCO2e": "kgCO2e",
}

_MASS_ALIASES   = {"kg", "t", "metric_ton", "mg"}
_VOLUME_ALIASES = {"l", "liter", "m3", "meter3", "meter ** 3"}
_ENERGY_ALIASES = {"mj", "gj", "kwh", "mwh"}

@dataclass
class FuelSpec:
    """
    Parametry fizyczne paliwa przekazywane z modelu Django.
    """
    density_kg_per_m3: Optional[float] = None   # gęstość [kg/m³]
    calorific_mj_per_kg: Optional[float] = None # wartość opałowa [MJ/kg]
    calorific_mj_per_m3: Optional[float] = None # wartość opałowa [MJ/m³]


def _resolve(unit_str: str) -> str:
    """Zamienia nazwę jednostki na nazwę rozumianą przez pint."""
    unit_str = unit_str.strip()
    if unit_str in _UNIT_ALIASES:
        return _UNIT_ALIASES[unit_str]
    return unit_str

def convert(value: float | int, unit_from: str, unit_to: str) -> float:
    """
    Przelicza wartość z jednostki source na docelową.

    Args:
        value:     liczba do przeliczenia
        unit_from: jednostka źródłowa (np. "kWh", "l", "kg")
        unit_to:   jednostka docelowa (np. "MWh", "m3", "t")

    Returns:
        Przeliczona wartość jako float.

    Raises:
        pint.DimensionalityError: jednostki są niekompatybilne
        pint.UndefinedUnitError:  nieznana jednostka
    """
    q = Q_(float(value), _resolve(unit_from))
    return q.to(_resolve(unit_to)).magnitude


def parse_factor_unit(unit_factor: str) -> tuple[str, str | None]:
    """
    Parsuje jednostkę wskaźnika emisji np. "tCO2e/MWh" → ("tCO2e", "MWh").

    Obsługuje formaty:
        "tCO2e/MWh"   → ("tCO2e", "MWh")
        "kgCO2e/l"    → ("kgCO2e", "l")
        "tCO2e"       → ("tCO2e", None)   ← wskaźnik bez mianownika

    Returns:
        (numerator_unit, denominator_unit | None)
    """
    unit_factor = unit_factor.strip()
    if "/" in unit_factor:
        num, den = unit_factor.split("/", 1)
        return num.strip(), den.strip()
    return unit_factor, None

def convert_via_fuel(
    value: float | int,
    unit_from: str,
    unit_to: str,
    fuel_spec: FuelSpec | None = None,
) -> float:
    """
    Przelicza wartość z unit_from na unit_to używając parametrów fizycznych paliwa.
    Jeśli fuel_spec jest None lub konwersja nie wymaga parametrów — deleguje do convert().

    Obsługiwane ścieżki:
        Masa → Objętość  (przez gęstość)
        Objętość → Masa  (przez gęstość)
        Masa → Energia   (przez wartość opałową MJ/kg)
        Objętość → Energia (przez wartość opałową MJ/l lub MJ/m³)

    Args:
        value:      ilość do przeliczenia
        unit_from:  jednostka źródłowa
        unit_to:    jednostka docelowa
        fuel_spec:  parametry fizyczne paliwa (opcjonalnie)

    Raises:
        ValueError: gdy brakuje wymaganego parametru w fuel_spec
    """
    if fuel_spec is None:
        return convert(value, unit_from, unit_to)

    uf = _resolve(unit_from).lower()
    ut = _resolve(unit_to).lower()

    from_mass = uf in _MASS_ALIASES
    to_mass   = ut in _MASS_ALIASES
    from_vol  = uf in _VOLUME_ALIASES
    to_vol    = ut in _VOLUME_ALIASES
    to_energy = ut in _ENERGY_ALIASES

    if from_vol and to_mass:
        if uf in ("m3", "meter3", "meter ** 3"):
            if fuel_spec.density_kg_per_m3 is None:
                raise ValueError("Brak gęstości kg/m3 w fuel_spec")
            mass_kg = float(value) * fuel_spec.density_kg_per_m3
        else:
            return convert(value, unit_from, unit_to)
        return convert(mass_kg, "kg", unit_to)

    if from_mass and to_vol:
        mass_kg = convert(value, unit_from, "kg")
        if ut in ("m3", "meter3", "meter ** 3"):
            if fuel_spec.density_kg_per_m3 is None:
                raise ValueError("Brak gęstości kg/m3 w fuel_spec")
            volume_m3 = mass_kg / fuel_spec.density_kg_per_m3
            return convert(volume_m3, "m3", unit_to)

    if from_mass and to_energy:
        mass_kg = convert(value, unit_from, "kg")
        if fuel_spec.calorific_mj_per_kg is None:
            raise ValueError("Brak wartości opałowej MJ/kg w fuel_spec")
        energy_mj = mass_kg * fuel_spec.calorific_mj_per_kg
        return convert(energy_mj, "MJ", unit_to)

    if from_vol and to_energy:
        if uf in ("m3", "meter3", "meter ** 3"):
            if fuel_spec.calorific_mj_per_m3 is None:
                raise ValueError("Brak wartości opałowej MJ/m3 w fuel_spec")
            energy_mj = float(value) * fuel_spec.calorific_mj_per_m3
        else:
            return convert(value, unit_from, unit_to)
        return convert(energy_mj, "MJ", unit_to)

    return convert(value, unit_from, unit_to)


def calculate_emission(
    amount: float | int,
    unit: str,
    factor_value: float,
    unit_factor: str,
    fuel_spec: FuelSpec | None = None,
) -> float:
    """
    Oblicza emisję CO2e dla pojedynczego rekordu.

    Logika:
        1. Parsuje jednostkę wskaźnika → (tCO2e, MWh)
        2. Konwertuje 'amount' z 'unit' na jednostkę mianownika wskaźnika
           (przez parametry paliwa jeśli trzeba)
        3. Mnoży przez wartość wskaźnika
        4. Konwertuje wynik do tCO2e

    Args:
        amount:       ilość (np. 500)
        unit:         jednostka ilości (np. "MWh", "l", "t")
        factor_value: wartość wskaźnika emisji (np. 0.82)
        unit_factor:  jednostka wskaźnika (np. "tCO2e/MWh")
        fuel_spec:    parametry fizyczne paliwa (np. gęstość) — opcjonalnie

    Returns:
        Emisja w tCO2e jako float.
    """
    num_unit_str, den_unit_str = parse_factor_unit(unit_factor)

    # Jeśli wskaźnik nie ma mianownika (np. "tCO2e") — brak konwersji ilości
    if den_unit_str is None:
        converted_amount = float(amount)
    else:
        converted_amount = convert_via_fuel(amount, unit, den_unit_str, fuel_spec)

    raw_emission = converted_amount * factor_value
    return convert(raw_emission, num_unit_str, "tCO2e")