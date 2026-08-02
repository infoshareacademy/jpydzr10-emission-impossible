from django.test import TestCase
from pint import DimensionalityError, UndefinedUnitError

from calculator.units import (
    convert,
    convert_via_fuel,
    parse_factor_unit,
    FuelSpec,
    Q_,
    ureg,
)


class ConvertBasicTests(TestCase):
    """Testy podstawowych konwersji jednostek przez pint."""

    def test_energy_mwh_to_kwh(self):
        self.assertAlmostEqual(convert(1, "MWh", "kWh"), 1000.0)

    def test_energy_gj_to_mj(self):
        self.assertAlmostEqual(convert(2, "GJ", "MJ"), 2000.0)

    def test_mass_t_to_kg(self):
        self.assertAlmostEqual(convert(5, "t", "kg"), 5000.0)

    def test_mass_mg_to_kg(self):
        self.assertAlmostEqual(convert(1, "Mg", "kg"), 1000.0)

    def test_volume_m3_to_liter(self):
        self.assertAlmostEqual(convert(3, "m3", "l"), 3000.0)

    def test_tco2e_to_kgco2e(self):
        self.assertAlmostEqual(convert(2.5, "tCO2e", "kgCO2e"), 2500.0)

    def test_kgco2e_to_tco2e(self):
        self.assertAlmostEqual(convert(500, "kgCO2e", "tCO2e"), 0.5)

    def test_integer_input(self):
        self.assertIsInstance(convert(100, "kWh", "MWh"), float)

    def test_float_input(self):
        self.assertAlmostEqual(convert(1.5, "MWh", "kWh"), 1500.0)

    def test_incompatible_units_raises_dimensionality_error(self):
        with self.assertRaises(DimensionalityError):
            convert(10, "kg", "m3")

    def test_unknown_unit_raises_undefined_unit_error(self):
        with self.assertRaises(UndefinedUnitError):
            convert(10, "xyz", "kg")


class ParseFactorUnitTests(TestCase):
    """Testy parsowania jednostek wskaźnika emisji."""

    def test_full_factor(self):
        num, den = parse_factor_unit("tCO2e/MWh")
        self.assertEqual(num, "tCO2e")
        self.assertEqual(den, "MWh")

    def test_factor_with_spaces(self):
        num, den = parse_factor_unit("  kgCO2e / l  ")
        self.assertEqual(num, "kgCO2e")
        self.assertEqual(den, "l")

    def test_factor_without_denominator(self):
        num, den = parse_factor_unit("tCO2e")
        self.assertEqual(num, "tCO2e")
        self.assertIsNone(den)

    def test_factor_multiple_slashes(self):
        num, den = parse_factor_unit("kgCO2e/m3/h")
        self.assertEqual(num, "kgCO2e")
        self.assertEqual(den, "m3/h")

    def test_empty_string(self):
        num, den = parse_factor_unit("")
        self.assertEqual(num, "")
        self.assertIsNone(den)


class ConvertViaFuelTests(TestCase):
    """Testy konwersji z wykorzystaniem parametrów paliwa."""

    def setUp(self):
        self.fuel = FuelSpec(
            density_kg_per_m3=850.0,  # np. olej opałowy
            calorific_mj_per_kg=42.7,
            calorific_mj_per_m3=36300.0,
        )

    def test_no_fuel_spec_delegates_to_convert(self):
        """Bez fuel_spec funkcja powinna delegować do zwykłego convert()."""
        result = convert_via_fuel(1000, "kWh", "MWh", None)
        self.assertAlmostEqual(result, 1.0)

    def test_volume_m3_to_mass_kg(self):
        """m3 -> kg przez gęstość."""
        result = convert_via_fuel(2, "m3", "kg", self.fuel)
        self.assertAlmostEqual(result, 1700.0)  # 2 * 850

    def test_volume_m3_to_mass_t(self):
        """m3 -> t przez gęstość."""
        result = convert_via_fuel(10, "m3", "t", self.fuel)
        self.assertAlmostEqual(result, 8.5)  # 10 * 850 / 1000

    def test_mass_kg_to_volume_m3(self):
        """kg -> m3 przez gęstość."""
        result = convert_via_fuel(850, "kg", "m3", self.fuel)
        self.assertAlmostEqual(result, 1.0)

    def test_mass_t_to_volume_m3(self):
        """t -> m3 przez gęstość."""
        result = convert_via_fuel(1, "t", "m3", self.fuel)
        self.assertAlmostEqual(result, 1000.0 / 850.0, places=5)

    def test_mass_kg_to_energy_mj(self):
        """kg -> MJ przez wartość opałową MJ/kg."""
        result = convert_via_fuel(10, "kg", "MJ", self.fuel)
        self.assertAlmostEqual(result, 427.0)  # 10 * 42.7

    def test_mass_kg_to_energy_gj(self):
        """kg -> GJ przez wartość opałową MJ/kg."""
        result = convert_via_fuel(1000, "kg", "GJ", self.fuel)
        self.assertAlmostEqual(result, 42.7)

    def test_volume_m3_to_energy_mj(self):
        """m3 -> MJ przez wartość opałową MJ/m3."""
        result = convert_via_fuel(1, "m3", "MJ", self.fuel)
        self.assertAlmostEqual(result, 36300.0)

    def test_volume_m3_to_energy_gj(self):
        """m3 -> GJ przez wartość opałową MJ/m3."""
        result = convert_via_fuel(1, "m3", "GJ", self.fuel)
        self.assertAlmostEqual(result, 36.3)

    def test_volume_liters_falls_back_to_convert(self):
        """l -> kg bez obsługi gęstości dla litrów (fallback do pint)."""
        result = convert_via_fuel(1000, "l", "m3", self.fuel)
        self.assertAlmostEqual(result, 1.0)

    def test_missing_density_for_m3_to_mass(self):
        """Brak gęstości przy konwersji m3 -> masa."""
        fuel_no_density = FuelSpec(calorific_mj_per_kg=42.0)
        with self.assertRaises(ValueError) as ctx:
            convert_via_fuel(1, "m3", "kg", fuel_no_density)
        self.assertIn("gęstości", str(ctx.exception).lower())

    def test_missing_density_for_mass_to_m3(self):
        """Brak gęstości przy konwersji masa -> m3."""
        fuel_no_density = FuelSpec(calorific_mj_per_kg=42.0)
        with self.assertRaises(ValueError) as ctx:
            convert_via_fuel(1000, "kg", "m3", fuel_no_density)
        self.assertIn("gęstości", str(ctx.exception).lower())

    def test_missing_calorific_mj_per_kg(self):
        """Brak wartości opałowej MJ/kg przy konwersji masa -> energia."""
        fuel_no_cal = FuelSpec(density_kg_per_m3=850.0)
        with self.assertRaises(ValueError) as ctx:
            convert_via_fuel(10, "kg", "MJ", fuel_no_cal)
        self.assertIn("opałowej", str(ctx.exception).lower())

    def test_missing_calorific_mj_per_m3(self):
        """Brak wartości opałowej MJ/m3 przy konwersji m3 -> energia."""
        fuel_no_cal = FuelSpec(density_kg_per_m3=850.0)
        with self.assertRaises(ValueError) as ctx:
            convert_via_fuel(1, "m3", "MJ", fuel_no_cal)
        self.assertIn("opałowej", str(ctx.exception).lower())

    def test_unsupported_path_falls_back(self):
        """Nieobsługiwana ścieżka (np. energia -> masa) deleguje do convert()."""
        with self.assertRaises(DimensionalityError):
            convert_via_fuel(100, "MJ", "kg", self.fuel)

    def test_meter3_alias(self):
        """Alias 'meter3' dla m3."""
        result = convert_via_fuel(1, "meter3", "kg", self.fuel)
        self.assertAlmostEqual(result, 850.0)


class UnitAliasesTests(TestCase):
    """Testy aliasów jednostek."""

    def test_mwh_alias(self):
        self.assertAlmostEqual(convert(1, "MWh", "kWh"), 1000.0)

    def test_mg_alias(self):
        self.assertAlmostEqual(convert(1, "Mg", "kg"), 1000.0)

    def test_m3_alias(self):
        self.assertAlmostEqual(convert(1, "m3", "l"), 1000.0)


class QuantityRegistryTests(TestCase):
    """Testy samego obiektu Quantity i UnitRegistry."""

    def test_quantity_creation(self):
        q = Q_(10, "m3")
        self.assertEqual(q.magnitude, 10)

    def test_ureg_has_custom_units(self):
        self.assertTrue(hasattr(ureg, "tCO2e"))
        self.assertTrue(hasattr(ureg, "kgCO2e"))
        self.assertTrue(hasattr(ureg, "m3"))
        self.assertTrue(hasattr(ureg, "Mg"))
