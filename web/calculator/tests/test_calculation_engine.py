from decimal import Decimal

from companies.models import Companies, CompaniesGroup, Countries
from django.core.exceptions import ValidationError
from django.test import TestCase
from emissions.models import EmissionFactor, EnergyPurchased, StationaryCombustion

from calculator.calculation import calculate_record_emissions
from calculator.models import FuelSpec, FuelType


class CalculationEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Inicjalizacja danych referencyjnych dla wszystkich testów.
        Wykonuje się raz dla całej klasy, co drastycznie przyspiesza testy.
        """
        # 1. Firma testowa
        cls.country = Countries.objects.create(name="Polska", code_alfa_2="PL")

        cls.group = CompaniesGroup.objects.create(
            gk_name="Testowa Grupa Kapitałowa", lvl_in_structure=1
        )

        cls.company = Companies.objects.create(
            name="Test ESG Corp",
            country=cls.country,
            city="Warszawa",
            zip="00-000",
            phone="123456789",
            mail="test@esg.com",
            krs=1234567890,
            regon=123456789,
            nip="1234567890",
            capital_group_name=cls.group,
        )

        # 2. Wskaźniki emisji (EmissionFactors)
        EmissionFactor.objects.create(
            factor_name="Gaz ziemny",
            country="PL",
            year=2024,
            factor=Decimal("0.20"),
            unit_factor="tCO2e/MWh",  # Prosty wskaźnik
        )

        EmissionFactor.objects.create(
            factor_name="Węgiel kamienny",
            country="PL",
            year=2024,
            factor=Decimal("95.00"),
            unit_factor="kgCO2e/GJ",  # Złożony wskaźnik (wymaga przelicznika z masy na energię)
        )

        # 3. Typy Paliw i Parametry Fizyczne (FuelSpec)
        fuel_coal = FuelType.objects.create(
            name="Węgiel kamienny", symbol="WEG", category="solid"
        )

        # Definiujemy wartość opałową dla węgla (25 MJ/kg, co matematycznie równe jest 25 GJ/t)
        FuelSpec.objects.create(
            fuel_type=fuel_coal,
            is_default=True,
            calorific_mj_per_kg=25.0,
            density_kg_per_m3=800.0,
        )

    def test_simple_calculation_without_conversion(self):
        """
        SCENARIUSZ 1: Jednostka użytkownika i mianownik wskaźnika są identyczne.
        Oczekujemy czystego mnożenia, przelicznik jednostek musi wynosić 1.0.
        """
        record = StationaryCombustion(
            company=self.company,
            year=2024,
            fuel="Gaz ziemny",
            amount=Decimal("100.0"),
            unit="MWh",  # Zgodne z tCO2e/MWh
        )

        calculate_record_emissions(record)

        # 100 MWh * 0.20 tCO2e/MWh = 20 tCO2e
        self.assertEqual(record.calculated_emission_tco2eq, Decimal("20.000"))

        # Weryfikacja śladu audytowego
        self.assertEqual(record.applied_factor_value, Decimal("0.20"))
        self.assertEqual(record.applied_factor_unit, "tCO2e/MWh")
        self.assertEqual(record.applied_converter_value, Decimal("1.00000"))
        self.assertEqual(record.applied_converter_unit, "MWh/MWh")

    def test_simple_physical_conversion(self):
        """
        SCENARIUSZ 2: Użytkownik podaje w kWh, a wskaźnik jest w MWh.
        System musi sam wykryć wymiar i podzielić przez 1000, budując ślad audytowy.
        """
        record = StationaryCombustion(
            company=self.company,
            year=2024,
            fuel="Gaz ziemny",
            amount=Decimal("5000.0"),
            unit="kWh",
        )

        calculate_record_emissions(record)

        # 5000 kWh = 5 MWh. 5 MWh * 0.20 tCO2e/MWh = 1.0 tCO2e
        self.assertEqual(record.calculated_emission_tco2eq, Decimal("1.000"))

        # Weryfikacja śladu audytowego - kluczowe dla audytora!
        self.assertEqual(record.applied_converter_value, Decimal("0.001"))
        self.assertEqual(record.applied_converter_unit, "MWh/kWh")

    def test_complex_calorific_conversion(self):
        """
        SCENARIUSZ 3: Masa (t) -> Energia (GJ) przy użyciu parametru FuelSpec.
        To testuje naszą najtrudniejszą ścieżkę fizyczną z units.py.
        """
        record = StationaryCombustion(
            company=self.company,
            year=2024,
            fuel="Węgiel kamienny",
            amount=Decimal("10.0"),
            unit="t",
        )

        calculate_record_emissions(record)

        # Krok 1: 10 t * 25.0 GJ/t (wartość opałowa) = 250 GJ
        # Krok 2: 250 GJ * 95.0 kgCO2e/GJ = 23750 kgCO2e
        # Krok 3: 23750 kgCO2e -> 23.75 tCO2e

        self.assertEqual(record.calculated_emission_tco2eq, Decimal("23.750"))

        # Weryfikacja twardego dowodu analitycznego
        self.assertEqual(record.applied_converter_value, Decimal("25.00000"))
        self.assertEqual(record.applied_converter_unit, "GJ/t")
        self.assertEqual(record.applied_factor_value, Decimal("95.00"))
        self.assertEqual(record.applied_factor_unit, "kgCO2e/GJ")

    def test_missing_fuel_spec_raises_validation_error(self):
        """
        SCENARIUSZ 4: Użytkownik podaje objętość dla paliwa, które nie ma gęstości w DB.
        System musi przerwać obliczenia i zwrócić jasny błąd.
        """
        # Celowo używamy węgla, który ma gęstość i opałowość,
        # ale spróbujemy z jednostki, której nie da się logicznie powiązać bez błędu
        # (np. przeliczamy energię z litrów, ale nie zdefiniowaliśmy gęstości płynu)

        # Dla testu stwórzmy paliwo bez zdefiniowanego FuelSpec
        EmissionFactor.objects.create(
            factor_name="Drewno opałowe",
            year=2024,
            factor=Decimal("100"),
            unit_factor="kgCO2e/GJ",
        )

        record = StationaryCombustion(
            company=self.company,
            year=2024,
            fuel="Drewno opałowe",
            amount=Decimal("5.0"),
            unit="t",
        )

        with self.assertRaisesMessage(ValidationError, "Cannot convert from"):
            calculate_record_emissions(record)

    def test_energy_purchased_custom_factor_priority(self):
        """
        SCENARIUSZ 5: Polimorfizm. Sprawdzamy czy klasa EnergyPurchased prawidłowo
        nadpisuje systemowe wskaźniki, gdy użytkownik wpisał własny mnożnik z faktury.
        """
        record = EnergyPurchased(
            company=self.company,
            year=2024,
            energy_type="Energia elektryczna",
            amount=Decimal("100.0"),
            unit="MWh",
            factor=Decimal("0.55"),  # UŻYTKOWNIK WPISAŁ WŁASNY WSKAŹNIK OD TAURONA
        )

        calculate_record_emissions(record)

        # 100 MWh * 0.55 = 55.0 tCO2e. Systemowy wskaźnik ma zostać zignorowany!
        self.assertAlmostEqual(float(record.calculated_emission_tco2eq), 55.0, places=3)
        self.assertEqual(record.applied_factor_value, Decimal("0.55"))
