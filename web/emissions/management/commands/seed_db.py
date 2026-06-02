import random
from decimal import Decimal

# Założenie: UserCompanyPermission znajduje się w aplikacji, w której masz CustomUser
# Jeśli masz to w innym pliku, zaktualizuj poniższy import
from accounts.models import UserCompanyPermission

# Importy modeli - upewnij się, że ścieżki (np. accounts.models) są zgodne z Twoją strukturą
from companies.models import Companies, CompaniesGroup, Countries
from django.contrib.auth import get_user_model
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
    RecordStatus,
    ReductionTarget,
    StationaryCombustion,
)

User = get_user_model()


# TO JEST KLASA, KTÓREJ BRAKOWAŁO DJANGO:
class Command(BaseCommand):
    help = "Zasila bazę danych testowymi danymi dla aplikacji Emission Impossible"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Rozpoczynam generowanie danych..."))

        # 1. GENEROWANIE UŻYTKOWNIKÓW
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "role": "admin",
                "is_superuser": True,
                "is_staff": True,
            },
        )
        admin.set_password("admin123")
        admin.save()

        user1, _ = User.objects.get_or_create(
            username="jkowalski",
            defaults={"email": "jkowalski@example.com", "role": "użytkownik"},
        )
        user1.set_password("test1234")
        user1.save()

        # 2. GENEROWANIE STRUKTURY FIRM
        country, _ = Countries.objects.get_or_create(
            code_alfa_2="PL", defaults={"name": "Polska"}
        )
        group, _ = CompaniesGroup.objects.get_or_create(
            gk_name="Grupa Kapitałowa Test", lvl_in_structure=1
        )

        company1, _ = Companies.objects.get_or_create(
            nip="1112223344",
            defaults={
                "name": "Fabryka Emisji Sp. z o.o.",
                "country": country,
                "city": "Gdańsk",
                "zip": "80-000",
                "phone": "123456789",
                "mail": "kontakt@fabryka.pl",
                "krs": 1111111111,
                "regon": 111111111,
                "capital_group_name": group,
            },
        )

        # Nadanie uprawnień użytkownikowi do firmy
        UserCompanyPermission.objects.get_or_create(
            user=user1, company=company1, defaults={"can_save": True, "can_read": True}
        )

        # 3. LISTY POMOCNICZE DO LOSOWANIA
        years = [2022, 2023, 2024]
        statuses = [
            RecordStatus.DRAFT,
            RecordStatus.PENDING,
            RecordStatus.APPROVED,
            RecordStatus.VERIFIED,
            RecordStatus.REJECTED,
        ]

        fuels_stationary = ["Gaz ziemny", "Węgiel kamienny", "Olej opałowy", "Pellet"]
        fuels_mobile = ["Olej napędowy (ON)", "Benzyna (Pb95)", "LPG", "CNG"]
        energy_types = [
            "Energia elektryczna z OZE",
            "Energia elektryczna nie OZE",
            "Ciepło z OZE",
            "Ciepło nie OZE",
        ]

        def rand_decimal(min_val, max_val):
            return Decimal(random.uniform(min_val, max_val)).quantize(Decimal("0.001"))

        # 4. GENEROWANIE DANYCH DLA ZAKRESU 1 (~20 rekordów na tabelę)
        self.stdout.write("Generowanie danych Zakresu 1...")
        for i in range(20):
            StationaryCombustion.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(10, 5000),
                unit=random.choice(["m3", "Mg", "litry"]),
                source=f"Faktura {i}/2023",
                fuel=random.choice(fuels_stationary),
                installation=f"Kocioł nr {random.randint(1, 5)} hala {random.choice(['A', 'B', 'C'])}",
                emission_tco2eq=rand_decimal(1, 100),
                notes="Wpis wygenerowany automatycznie",
            )

            MobileCombustion.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(50, 2000),
                unit="litry",
                source=f"Raport floty {i}",
                fuel=random.choice(fuels_mobile),
                vehicle=f"Pojazd {random.choice(['Osobowy', 'Dostawczy', 'Wózek widłowy'])} - {random.randint(100, 999)}",
                emission_tco2eq=rand_decimal(0.5, 20),
            )

            ProcessEmission.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(5, 50),
                unit="tony",
                source="Raport technologiczny",
                process=f"Proces chemiczny typu {random.choice(['A', 'B', 'X'])}",
                product=f"Produkt końcowy {random.randint(1, 100)}",
                emission_tco2eq=rand_decimal(10, 150),
            )

            FugitiveEmission.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(1, 15),
                unit="kg",
                source="Karta Urządzenia",
                installation=f"Klimatyzator biurowy nr {random.randint(1, 20)}",
                product=random.choice(["R410A", "R134a", "SF6"]),
                emission_tco2eq=rand_decimal(2, 30),
            )

        # 5. GENEROWANIE DANYCH DLA ZAKRESU 2 (Energia)
        self.stdout.write("Generowanie danych Zakresu 2...")
        for i in range(20):
            EnergyConsumption.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(1000, 50000),
                unit=random.choice(["kWh", "MWh", "GJ"]),
                source="Liczniki wewnętrzne",
                energy_source=random.choice(["Zakupiona", "Wyprodukowana"]),
                energy_type=random.choice(energy_types),
                emission_tco2eq=rand_decimal(5, 200),
            )

            EnergyPurchased.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
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
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(100, 2000),
                unit="MWh",
                source="System SCADA",
                installation=f"Instalacja Fotowoltaiczna na dachu {random.choice(['Hali A', 'Biura'])}",
                energy_type="Energia elektryczna z OZE",
                factor=rand_decimal(0, 0.05),
            )

            EnergySold.objects.create(
                year=random.choice(years),
                company=company1,
                status=random.choice(statuses),
                amount=rand_decimal(50, 500),
                unit="MWh",
                source="Faktury sprzedażowe",
                customer=f"Odbiorca Zewnętrzny {random.randint(1, 5)}",
                energy_type="Energia elektryczna z OZE",
            )

        # 6. SŁOWNIKI I DANE KONFIGURACYJNE
        self.stdout.write("Generowanie wskaźników i logów...")
        for i in range(5):
            EmissionFactor.objects.create(
                factor_name=f"Wskaźnik KOBiZE {2020 + i}",
                country="PL",
                year=2020 + i,
                factor=rand_decimal(0.5, 1.5),
                unit_factor="kgCO2e/kWh",
                source="Raport KOBiZE",
            )

            ReductionTarget.objects.create(
                company=company1.name,
                target_name=f"Cel dekarbonizacji {i + 1}",
                base_year=2021,
                target_year=2030,
                reduction_pct=Decimal(random.randint(10, 50)),
                scope=random.choice(["1", "2", "1+2", "3"]),
            )

        self.stdout.write(self.style.SUCCESS("Pomyślnie wygenerowano testowe dane!"))
