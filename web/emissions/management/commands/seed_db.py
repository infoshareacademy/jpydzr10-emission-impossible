import random
from decimal import Decimal

from accounts.models import UserCompanyPermission
from calculator.calculation import calculate_record_emissions
from calculator.models import FuelSpec, FuelType, Supplier
from companies.models import Companies, CompaniesGroup, Countries
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from emissions.models import (
    EmissionFactor,
    EnergyConsumption,
    EnergyProduced,
    EnergyPurchased,
    EnergySold,
    FugitiveEmission,
    MobileCombustion,
    ProcessEmission,
    StationaryCombustion,
)
from workflow.models import WorkflowStatusMixin

RecordStatus = WorkflowStatusMixin.RecordStatus

User = get_user_model()


class Command(BaseCommand):
    help = "Zasila bazę danych testowymi danymi dla aplikacji Emission Impossible"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Rozpoczynam generowanie danych..."))

        # =====================================================================
        # 1. UŻYTKOWNICY
        # =====================================================================
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "role": "admin",
                "is_superuser": True,
                "is_staff": True,
            },
        )
        if not admin.check_password("admin123"):
            admin.set_password("admin123")
            admin.save()

        user1, _ = User.objects.get_or_create(
            username="jkowalski",
            defaults={"email": "jkowalski@example.com", "role": "użytkownik"},
        )
        if not user1.check_password("test1234"):
            user1.set_password("test1234")
            user1.save()

        user2, _ = User.objects.get_or_create(
            username="anowak",
            defaults={"email": "anowak@example.com", "role": "audytor"},
        )
        if not user2.check_password("test1234"):
            user2.set_password("test1234")
            user2.save()

        # =====================================================================
        # 2. STRUKTURA FIRM
        # =====================================================================
        poland, _ = Countries.objects.get_or_create(
            code_alfa_2="PL", defaults={"name": "Polska"}
        )
        germany, _ = Countries.objects.get_or_create(
            code_alfa_2="DE", defaults={"name": "Niemcy"}
        )

        group, _ = CompaniesGroup.objects.get_or_create(
            gk_name="Grupa Kapitałowa Test", defaults={"lvl_in_structure": 1}
        )
        group2, _ = CompaniesGroup.objects.get_or_create(
            gk_name="Holding Przemysłowy", defaults={"lvl_in_structure": 2}
        )

        company1, _ = Companies.objects.get_or_create(
            nip="1112223344",
            defaults={
                "name": "Fabryka Emisji Sp. z o.o.",
                "country": poland,
                "city": "Gdańsk",
                "zip": "80-000",
                "phone": "123456789",
                "mail": "kontakt@fabryka.pl",
                "krs": 1111111111,
                "regon": 111111111,
                "capital_group_name": group,
            },
        )

        company2, _ = Companies.objects.get_or_create(
            nip="5556667788",
            defaults={
                "name": "Energetyka Polska S.A.",
                "country": poland,
                "city": "Warszawa",
                "zip": "00-001",
                "phone": "987654321",
                "mail": "biuro@energetyka.pl",
                "krs": 222222222,  # 9 cyfr — mieści się w integer
                "regon": 222222222,
                "capital_group_name": group,
            },
        )

        company3, _ = Companies.objects.get_or_create(
            nip="9990001112",
            defaults={
                "name": "Logistyka Centrum Sp. z o.o.",
                "country": poland,
                "city": "Kraków",
                "zip": "30-001",
                "phone": "111222333",
                "mail": "info@logistyka.pl",
                "krs": 333333333,  # 9 cyfr
                "regon": 333333333,
                "capital_group_name": group2,
            },
        )

        companies = [company1, company2, company3]

        # Uprawnienia użytkowników
        for company in companies:
            UserCompanyPermission.objects.get_or_create(
                user=admin,
                company=company,
                defaults={"can_save": True, "can_read": True},
            )
        UserCompanyPermission.objects.get_or_create(
            user=user1, company=company1, defaults={"can_save": True, "can_read": True}
        )
        UserCompanyPermission.objects.get_or_create(
            user=user1, company=company2, defaults={"can_save": False, "can_read": True}
        )
        UserCompanyPermission.objects.get_or_create(
            user=user2, company=company2, defaults={"can_save": False, "can_read": True}
        )
        UserCompanyPermission.objects.get_or_create(
            user=user2, company=company3, defaults={"can_save": False, "can_read": True}
        )

        # =====================================================================
        # 3. LISTY POMOCNICZE
        # =====================================================================
        years = [2022, 2023, 2024]
        statuses = [
            RecordStatus.DRAFT,
            RecordStatus.PENDING,
            RecordStatus.APPROVED,
            RecordStatus.REJECTED,
        ]

        fuels_stationary = ["Gaz ziemny", "Węgiel kamienny", "Pellet drzewny"]
        fuels_mobile = ["Olej napędowy (ON)", "Benzyna (Pb95)", "LPG"]
        energy_types = [
            "Energia elektryczna z OZE",
            "Energia elektryczna nie OZE",
            "Ciepło z OZE",
            "Ciepło nie OZE",
        ]

        def rand_decimal(min_val, max_val):
            return Decimal(random.uniform(min_val, max_val)).quantize(Decimal("0.001"))

        # =====================================================================
        # 3.5. SŁOWNIKI (PALIWA, DOSTAWCY, SPECYFIKACJE)
        # =====================================================================
        self.stdout.write("Generowanie słowników (Paliwa, Dostawcy, Specyfikacje)...")

        supplier_orlen, _ = Supplier.objects.get_or_create(name="Orlen S.A.")
        supplier_pgnig, _ = Supplier.objects.get_or_create(name="PGNiG")
        supplier_pgg, _ = Supplier.objects.get_or_create(name="Polska Grupa Górnicza")

        fuel_diesel, _ = FuelType.objects.get_or_create(
            symbol="ON", defaults={"name": "Olej napędowy (ON)", "category": "liquid"}
        )
        fuel_petrol, _ = FuelType.objects.get_or_create(
            symbol="PB95", defaults={"name": "Benzyna (Pb95)", "category": "liquid"}
        )
        fuel_lpg, _ = FuelType.objects.get_or_create(
            symbol="LPG", defaults={"name": "LPG", "category": "gas"}
        )
        fuel_gas, _ = FuelType.objects.get_or_create(
            symbol="GAZ", defaults={"name": "Gaz ziemny", "category": "gas"}
        )
        fuel_coal, _ = FuelType.objects.get_or_create(
            symbol="WEG", defaults={"name": "Węgiel kamienny", "category": "solid"}
        )
        fuel_pellet, _ = FuelType.objects.get_or_create(
            symbol="PEL", defaults={"name": "Pellet drzewny", "category": "solid"}
        )

        fuel_type_map = {
            "Olej napędowy (ON)": fuel_diesel,
            "Benzyna (Pb95)": fuel_petrol,
            "LPG": fuel_lpg,
            "Gaz ziemny": fuel_gas,
            "Węgiel kamienny": fuel_coal,
            "Pellet drzewny": fuel_pellet,
        }

        # Domyślne specyfikacje
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_diesel,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 840.0,
                "calorific_mj_per_kg": 43.0,
                "calorific_mj_per_m3": None,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_petrol,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 750.0,
                "calorific_mj_per_kg": 44.3,
                "calorific_mj_per_m3": None,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_lpg,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 540.0,
                "calorific_mj_per_kg": 46.0,
                "calorific_mj_per_m3": None,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_gas,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 0.74,
                "calorific_mj_per_kg": None,
                "calorific_mj_per_m3": 36.0,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_coal,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 800.0,
                "calorific_mj_per_kg": 24.0,
                "calorific_mj_per_m3": None,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_pellet,
            supplier=None,
            defaults={
                "is_default": True,
                "density_kg_per_m3": 650.0,
                "calorific_mj_per_kg": 18.0,
                "calorific_mj_per_m3": None,
            },
        )

        # Specyficzne specyfikacje
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_diesel,
            supplier=supplier_orlen,
            defaults={
                "is_default": False,
                "density_kg_per_m3": 835.0,
                "calorific_mj_per_kg": 43.2,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_gas,
            supplier=supplier_pgnig,
            defaults={
                "is_default": False,
                "density_kg_per_m3": 0.73,
                "calorific_mj_per_m3": 37.5,
            },
        )
        FuelSpec.objects.get_or_create(
            fuel_type=fuel_coal,
            supplier=supplier_pgg,
            defaults={
                "is_default": False,
                "density_kg_per_m3": 810.0,
                "calorific_mj_per_kg": 25.5,
            },
        )

        # =====================================================================
        # 3.6. WSKAŹNIKI EMISJI
        # =====================================================================
        self.stdout.write("Generowanie wskaźników emisji...")

        all_fuels = (
            fuels_stationary
            + fuels_mobile
            + [
                "R410A",
                "R134a",
                "SF6",
                "Proces chemiczny typu A",
                "Proces chemiczny typu B",
                "Proces chemiczny typu X",
            ]
        )

        for y in years:
            EmissionFactor.objects.get_or_create(
                factor_name=f"Wskaźnik KOBiZE {y}",
                country=poland,
                year=y,
                defaults={
                    "factor": rand_decimal(0.6, 0.8),
                    "unit_factor": "kgCO2e/kWh",
                    "source": "KOBiZE",
                },
            )
            for fuel_name in all_fuels:
                if fuel_name == "Gaz ziemny":
                    u_factor = "kgCO2e/m3"
                elif fuel_name in fuels_stationary:
                    u_factor = "kgCO2e/Mg"
                elif fuel_name in fuels_mobile:
                    u_factor = "kgCO2e/l"
                else:
                    u_factor = "kgCO2e/kg"

                EmissionFactor.objects.get_or_create(
                    factor_name=fuel_name,
                    country=poland,
                    year=y,
                    defaults={
                        "factor": rand_decimal(1.5, 2.9),
                        "unit_factor": u_factor,
                        "source": "KOBiZE",
                    },
                )

        # =====================================================================
        # 4. DANE ZAKRESU 1 — dla każdej spółki
        # =====================================================================
        self.stdout.write("Generowanie danych Zakresu 1...")

        for company in companies:
            self.stdout.write(f"  → {company.name}")
            for i in range(20):
                # Spalanie stacjonarne
                fuel_stat_name = random.choice(fuels_stationary)
                fuel_stat_fk = fuel_type_map[fuel_stat_name]
                unit_stat = (
                    "m3"
                    if fuel_stat_name == "Gaz ziemny"
                    else random.choice(["Mg", "t"])
                )

                stat_comb = StationaryCombustion(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(10, 5000),
                    unit=unit_stat,
                    source=f"Faktura {i}/2023",
                    fuel=fuel_stat_fk,
                    installation=f"Kocioł nr {random.randint(1, 5)} hala {random.choice(['A', 'B', 'C'])}",
                    emission_tco2eq=rand_decimal(1, 100),
                )
                try:
                    calculate_record_emissions(stat_comb)
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Błąd stat: {e}"))
                stat_comb.save()

                # Spalanie mobilne
                fuel_mob_name = random.choice(fuels_mobile)
                fuel_mob_fk = fuel_type_map[fuel_mob_name]

                mob_comb = MobileCombustion(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(50, 2000),
                    unit="l",
                    source=f"Raport floty {i}",
                    fuel=fuel_mob_fk,
                    vehicle=f"Pojazd {random.choice(['Osobowy', 'Dostawczy', 'Wózek widłowy'])} - {random.randint(100, 999)}",
                    emission_tco2eq=rand_decimal(0.5, 20),
                )
                try:
                    calculate_record_emissions(mob_comb)
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Błąd mob: {e}"))
                mob_comb.save()

                # Emisje procesowe
                proc_choice = random.choice(["A", "B", "X"])
                proc_emis = ProcessEmission(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(5, 50),
                    unit="t",
                    source="Raport technologiczny",
                    process=f"Proces chemiczny typu {proc_choice}",
                    product=f"Produkt końcowy {random.randint(1, 100)}",
                    emission_tco2eq=rand_decimal(10, 150),
                )
                try:
                    calculate_record_emissions(proc_emis)
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Błąd proc: {e}"))
                proc_emis.save()

                # Emisje niezorganizowane
                prod_choice = random.choice(["R410A", "R134a", "SF6"])
                fug_emis = FugitiveEmission(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(1, 15),
                    unit="kg",
                    source="Karta Urządzenia",
                    installation=f"Klimatyzator biurowy nr {random.randint(1, 20)}",
                    product=prod_choice,
                    emission_tco2eq=rand_decimal(2, 30),
                )
                try:
                    calculate_record_emissions(fug_emis)
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f"Błąd fug: {e}"))
                fug_emis.save()

        # =====================================================================
        # 5. DANE ZAKRESU 2 — dla każdej spółki
        # =====================================================================
        self.stdout.write("Generowanie danych Zakresu 2...")

        for company in companies:
            self.stdout.write(f"  → {company.name}")
            for i in range(20):
                EnergyConsumption.objects.create(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(1000, 50000),
                    unit=random.choice(["kWh", "MWh", "GJ"]),
                    source="Liczniki wewnętrzne",
                    energy_source=random.choice(["Zakupiona", "Wyprodukowana"]),
                    energy_type=random.choice(energy_types),
                    emission_tco2eq=rand_decimal(5, 200),
                )
                EnergyPurchased.objects.create(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(500, 10000),
                    unit="MWh",
                    source="Faktura od dostawcy",
                    trader=random.choice(["PGE", "Tauron", "Enea", "Energa"]),
                    energy_type=random.choice(energy_types),
                    factor=rand_decimal(0.1, 0.9),
                    emission_tco2eq=rand_decimal(10, 500),
                )
                EnergyProduced.objects.create(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(100, 2000),
                    unit="MWh",
                    source="System SCADA",
                    installation=f"Instalacja Fotowoltaiczna na dachu {random.choice(['Hali A', 'Biura'])}",
                    energy_type="Energia elektryczna z OZE",
                    factor=rand_decimal(0, 0.05),
                )
                EnergySold.objects.create(
                    year=random.choice(years),
                    company=company,
                    workflow_status=random.choice(statuses),
                    amount=rand_decimal(50, 500),
                    unit="MWh",
                    source="Faktury sprzedażowe",
                    customer=f"Odbiorca Zewnętrzny {random.randint(1, 5)}",
                    energy_type="Energia elektryczna z OZE",
                )

        self.stdout.write(
            self.style.SUCCESS("Pomyślnie wygenerowano testowe dane dla 3 spółek!")
        )