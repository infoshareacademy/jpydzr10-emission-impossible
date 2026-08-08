from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _  # <--- KLUCZOWY IMPORT DLA TŁUMACZEŃ
from emissions.models import EmissionFactor

from calculator.models import FuelSpec as DbFuelSpec
from calculator.units import (
    FuelSpec as DataclassFuelSpec,
)
from calculator.units import (
    convert_via_fuel,
    parse_factor_unit,
)


def calculate_record_emissions(instance) -> None:
    """
    Uniwersalna funkcja obliczeniowa dla WSZYSTKICH modeli Zakresu 1 i 2.
    Modyfikuje instancję 'in-place' dodając pełen ślad audytowy.
    Nie wywołuje metody .save() – robi to widok lub funkcja wywołująca.
    """
    model_name = instance.__class__.__name__

    lookup_mapping = {
        "StationaryCombustion": "fuel",
        "MobileCombustion": "fuel",
        "ProcessEmission": "process",
        "FugitiveEmission": "product",
        "EnergyConsumption": "energy_type",
        "EnergyPurchased": "energy_type",
        "EnergyProduced": "energy_type",
        "EnergySold": "energy_type",
    }

    lookup_field = lookup_mapping.get(model_name)
    if not lookup_field:
        raise ValueError(_("Nieobsługiwany model dla kalkulatora: %(model)s") % {"model": model_name})

    # Pobieramy wartość (np. "Węgiel kamienny", "Energia elektryczna")
    lookup_value = getattr(instance, lookup_field, None)

    # 2. Pobranie Wskaźnika z bazy
    factor_obj = EmissionFactor.objects.filter(
        factor_name=lookup_value,
        year=getattr(instance, "year", None),
        country=instance.company.country,
    ).first()

    # Zmienne startowe
    calculated_emission = Decimal("0.0")
    factor_value = Decimal("0.0")
    factor_unit = None
    converter_value = Decimal("1.00000")
    converter_unit = f"{instance.unit}/{instance.unit}"

    # --- SPECJALNY PRZYPADEK: Zakup/Produkcja Energii z własnym wskaźnikiem ---
    # Widzę w Twoich modelach, że EnergyPurchased ma pole `factor`.
    # Jeśli użytkownik wpisał tam własny wskaźnik od sprzedawcy (inny niż 0), używamy go!
    if hasattr(instance, "factor") and getattr(instance, "factor") > 0:
        factor_value = getattr(instance, "factor")
        factor_unit = f"tCO2e/{instance.unit}"  # Zakładamy domyślną jednostkę dla własnego wskaźnika
        raw_emission = float(instance.amount) * float(factor_value)
        calculated_emission = Decimal(str(raw_emission))

    # --- STANDARDOWY PRZYPADEK: Obliczanie na podstawie systemowego EmissionFactor ---
    elif factor_obj:
        factor_value = Decimal(str(factor_obj.factor))
        factor_unit = factor_obj.unit_factor
        num_unit, den_unit = parse_factor_unit(factor_unit)

        # 3. Pobranie parametrów fizycznych (TYLKO jeśli to paliwo)
        dataclass_fuel_spec = None
        if lookup_field == "fuel":
            db_fuel_spec = DbFuelSpec.objects.filter(
                fuel_type__name=lookup_value, is_default=True
            ).first()
            if db_fuel_spec:
                dataclass_fuel_spec = DataclassFuelSpec(
                    density_kg_per_m3=db_fuel_spec.density_kg_per_m3,
                    calorific_mj_per_kg=db_fuel_spec.calorific_mj_per_kg,
                    calorific_mj_per_m3=db_fuel_spec.calorific_mj_per_m3,
                )

        # 4. Wyliczanie mnożnika audytowego i konwersja ilości
        if den_unit is None or instance.unit == den_unit:
            normalized_amount = float(instance.amount)
        else:
            try:
                raw_multiplier = convert_via_fuel(
                    value=1.0,
                    unit_from=instance.unit,
                    unit_to=den_unit,
                    fuel_spec=dataclass_fuel_spec,
                )
                converter_value = Decimal(str(raw_multiplier))
                converter_unit = f"{den_unit}/{instance.unit}"
                normalized_amount = float(instance.amount) * raw_multiplier
            except Exception as e:
                raise ValidationError(
                    _("Błąd konwersji jednostek dla '%(lookup)s': %(error)s") % {
                        "lookup": lookup_value,
                        "error": str(e)
                    }
                )

        # 5. Właściwe wyliczenie i konwersja licznika na tony CO2e
        from calculator.units import convert

        raw_emission = normalized_amount * float(factor_value)
        final_emission_tco2e = convert(raw_emission, num_unit, "tCO2e")
        calculated_emission = Decimal(str(final_emission_tco2e))

    # 6. Zapis wyników do instancji (ślad audytowy)
    instance.calculated_emission_tco2eq = calculated_emission
    instance.applied_factor_value = factor_value
    instance.applied_factor_unit = factor_unit
    instance.applied_converter_value = converter_value
    instance.applied_converter_unit = converter_unit