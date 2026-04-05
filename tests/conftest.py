"""
Fixture'y testowe — tworzą tymczasowe pliki CSV z danymi testowymi.
Każdy test działa na izolowanej kopii danych (tmp_path).
"""

import csv
import os
import pytest
from decimal import Decimal

from app.application.use_cases import EmissionUseCases
from app.infrastructure.repositories.file.repositories import (
    RepositoryFactory, FactorRepository, ConverterRepository,
)


def _write_csv(path: str, fieldnames: list[str], rows: list[dict]):
    """Pomocnicza funkcja — zapisuje CSV z nagłówkami i wierszami."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


@pytest.fixture
def test_data_folder(tmp_path):
    """Tworzy tymczasowy folder z pełnym zestawem plików CSV do testów."""
    folder = str(tmp_path)

    # --- tbl_factors.csv ---
    _write_csv(os.path.join(folder, "tbl_factors.csv"),
        ["id", "factor_name", "country", "factor", "unit_factor", "source"],
        [
            {"id": 1, "factor_name": "gaz ziemny", "country": "Polska", "factor": "0.00202", "unit_factor": "tCO2e/m3", "source": "KOBiZE"},
            {"id": 2, "factor_name": "diesel", "country": "Polska", "factor": "0.00268", "unit_factor": "tCO2e/l", "source": "DEFRA"},
            {"id": 3, "factor_name": "benzyna", "country": "Polska", "factor": "0.00232", "unit_factor": "tCO2e/l", "source": "DEFRA"},
            {"id": 4, "factor_name": "LPG", "country": "Polska", "factor": "0.00163", "unit_factor": "tCO2e/l", "source": "DEFRA"},
            {"id": 5, "factor_name": "węgiel kamienny", "country": "Polska", "factor": "2.446", "unit_factor": "tCO2e/t", "source": "KOBiZE"},
            {"id": 6, "factor_name": "olej opałowy lekki", "country": "Polska", "factor": "3.17", "unit_factor": "tCO2e/t", "source": "KOBiZE"},
            {"id": 7, "factor_name": "olej opałowy ciężki", "country": "Polska", "factor": "3.17", "unit_factor": "tCO2e/t", "source": "KOBiZE"},
            {"id": 8, "factor_name": "R410A", "country": "Polska", "factor": "2088", "unit_factor": "kgCO2e/kg", "source": "IPCC"},
            {"id": 9, "factor_name": "R32", "country": "Polska", "factor": "675", "unit_factor": "kgCO2e/kg", "source": "IPCC"},
            {"id": 10, "factor_name": "kalcynacja", "country": "Polska", "factor": "0.780", "unit_factor": "tCO2e/t", "source": "IPCC"},
            {"id": 11, "factor_name": "Energia elektryczna nie OZE", "country": "Polska", "factor": "0.709", "unit_factor": "tCO2e/MWh", "source": "KOBiZE"},
            {"id": 12, "factor_name": "Energia elektryczna z OZE", "country": "Polska", "factor": "0.0", "unit_factor": "tCO2e/MWh", "source": "GO"},
            {"id": 13, "factor_name": "Energia cieplna", "country": "Polska", "factor": "0.292", "unit_factor": "tCO2e/GJ", "source": "KOBiZE"},
            {"id": 14, "factor_name": "Chłód", "country": "Polska", "factor": "0.180", "unit_factor": "tCO2e/GJ", "source": "KOBiZE"},
            {"id": 15, "factor_name": "biomasa", "country": "Polska", "factor": "0.0", "unit_factor": "tCO2e/t", "source": "neutralna"},
        ],
    )

    # --- tbl_converters.csv ---
    _write_csv(os.path.join(folder, "tbl_converters.csv"),
        ["id", "unit_from", "unit_to", "factor"],
        [
            {"id": 1, "unit_from": "MWh", "unit_to": "kWh", "factor": "1000"},
            {"id": 2, "unit_from": "MWh", "unit_to": "GJ", "factor": "3.6"},
            {"id": 3, "unit_from": "MWh", "unit_to": "MJ", "factor": "3600"},
            {"id": 4, "unit_from": "GJ", "unit_to": "MJ", "factor": "1000"},
            {"id": 5, "unit_from": "t", "unit_to": "kg", "factor": "1000"},
            {"id": 6, "unit_from": "Mg", "unit_to": "t", "factor": "1"},
            {"id": 7, "unit_from": "m3", "unit_to": "l", "factor": "1000"},
            {"id": 8, "unit_from": "kWh", "unit_to": "MJ", "factor": "3.6"},
            {"id": 9, "unit_from": "GJ", "unit_to": "kWh", "factor": "277.778"},
            {"id": 10, "unit_from": "Mg", "unit_to": "kg", "factor": "1000"},
            {"id": 11, "unit_from": "t", "unit_to": "g", "factor": "1000000"},
            {"id": 12, "unit_from": "kg", "unit_to": "g", "factor": "1000"},
        ],
    )

    # --- tbl_companies.csv ---
    _write_csv(os.path.join(folder, "tbl_companies.csv"),
        ["co_id", "co_name", "co_country", "co_city", "co_street", "co_zip",
         "co_tel", "co_mail", "co_krs", "co_regon", "co_nip", "cg_name"],
        [
            {"co_id": 0, "co_name": "TestFirma A", "co_country": "Polska",
             "co_city": "Warszawa", "co_street": "Testowa 1", "co_zip": "00-001",
             "co_tel": "+48 22 100 2000", "co_mail": "a@test.pl",
             "co_krs": "0000112233", "co_regon": "123456789", "co_nip": "5261234567",
             "cg_name": "TestGrupa"},
            {"co_id": 1, "co_name": "TestFirma B", "co_country": "Polska",
             "co_city": "Kraków", "co_street": "Testowa 2", "co_zip": "30-001",
             "co_tel": "+48 12 200 3000", "co_mail": "b@test.pl",
             "co_krs": "0000223344", "co_regon": "234567890", "co_nip": "6342345678",
             "cg_name": "TestGrupa"},
        ],
    )

    # --- tbl_stationary_combustion.csv ---
    _write_csv(os.path.join(folder, "tbl_stationary_combustion.csv"),
        ["id", "year", "company", "data_quality", "amount", "unit", "source", "fuel", "installation", "emission_tco2eq", "raport", "notes"],
        [
            # emission_tco2eq podana + raport → użyj deklarowanej wartości
            {"id": 1, "year": 2025, "company": "TestFirma A", "data_quality": "measured",
             "amount": "10000", "unit": "m3",
             "source": "faktura", "fuel": "gaz ziemny", "installation": "kotłownia",
             "emission_tco2eq": "99.999", "raport": "KOBiZE", "notes": ""},
            # emission_tco2eq puste → oblicz: 5000 m3 × 0.00202 = 10.100 tCO2e
            {"id": 2, "year": 2025, "company": "TestFirma A", "data_quality": "calculated",
             "amount": "5000", "unit": "m3",
             "source": "faktura", "fuel": "gaz ziemny", "installation": "piec",
             "emission_tco2eq": "", "raport": "", "notes": ""},
            # raport podany ale emission_tco2eq puste → walidacja powinna wyłapać
            {"id": 3, "year": 2025, "company": "TestFirma B", "data_quality": "estimated",
             "amount": "200", "unit": "t",
             "source": "faktura", "fuel": "węgiel kamienny", "installation": "kotłownia",
             "emission_tco2eq": "", "raport": "KOBiZE", "notes": ""},
            # Inny rok do testów trendów — deklarowana emisja
            {"id": 4, "year": 2024, "company": "TestFirma A", "data_quality": "measured",
             "amount": "12000", "unit": "m3",
             "source": "faktura", "fuel": "gaz ziemny", "installation": "kotłownia",
             "emission_tco2eq": "24.240", "raport": "KOBiZE", "notes": "pomiar kontrolny"},
        ],
    )

    # --- tbl_mobile_combustion.csv ---
    _write_csv(os.path.join(folder, "tbl_mobile_combustion.csv"),
        ["id", "year", "company", "data_quality", "amount", "unit", "source", "vehicle", "fuel", "emission_tco2eq", "raport", "notes"],
        [
            # 2400 l benzyna × 0.00232 = 5.568 tCO2e (brak deklarowanej emisji)
            {"id": 1, "year": 2025, "company": "TestFirma A", "data_quality": "calculated",
             "amount": "2400", "unit": "l",
             "source": "karty", "vehicle": "samochód osobowy", "fuel": "benzyna",
             "emission_tco2eq": "", "raport": "", "notes": ""},
            # 5000 l diesel × 0.00268 = 13.400 tCO2e (brak deklarowanej emisji)
            {"id": 2, "year": 2025, "company": "TestFirma A", "data_quality": "calculated",
             "amount": "5000", "unit": "l",
             "source": "karty", "vehicle": "samochód osobowy", "fuel": "diesel",
             "emission_tco2eq": "", "raport": "", "notes": ""},
            # 1000 l LPG × 0.00163 = 1.630 tCO2e (brak deklarowanej emisji)
            {"id": 3, "year": 2025, "company": "TestFirma B", "data_quality": "",
             "amount": "1000", "unit": "l",
             "source": "faktura", "vehicle": "wózek widłowy", "fuel": "LPG",
             "emission_tco2eq": "", "raport": "", "notes": ""},
            # Rok 2024 — deklarowana emisja
            {"id": 4, "year": 2024, "company": "TestFirma A", "data_quality": "measured",
             "amount": "3000", "unit": "l",
             "source": "karty", "vehicle": "samochód osobowy", "fuel": "diesel",
             "emission_tco2eq": "9.000", "raport": "DEFRA 2024", "notes": "pomiar flota"},
        ],
    )

    # --- tbl_fugitve_emissions.csv ---
    _write_csv(os.path.join(folder, "tbl_fugitve_emissions.csv"),
        ["id", "year", "company", "data_quality", "amount", "unit", "source", "installation", "product", "emission_tco2eq", "raport", "notes"],
        [
            # 5 kg R410A × 2088 kgCO2e/kg = 10440 kgCO2e = 10.440 tCO2e (brak deklarowanej)
            {"id": 1, "year": 2025, "company": "TestFirma A", "data_quality": "estimated",
             "amount": "5", "unit": "kg",
             "source": "serwis", "installation": "klimatyzacja biuro", "product": "R410A",
             "emission_tco2eq": "", "raport": "", "notes": ""},
            # 2 kg R32 × 675 kgCO2e/kg = 1350 kgCO2e = 1.350 tCO2e (brak deklarowanej)
            {"id": 2, "year": 2025, "company": "TestFirma B", "data_quality": "estimated",
             "amount": "2", "unit": "kg",
             "source": "serwis", "installation": "klimatyzacja hala", "product": "R32",
             "emission_tco2eq": "", "raport": "", "notes": ""},
        ],
    )

    # --- tbl_process_emissions.csv ---
    _write_csv(os.path.join(folder, "tbl_process_emissions.csv"),
        ["id", "year", "company", "data_quality", "amount", "unit", "source", "process", "product", "emission_tco2eq", "raport", "notes"],
        [
            # 100 t kalcynacja × 0.780 = 78.000 tCO2e (brak deklarowanej)
            {"id": 1, "year": 2025, "company": "TestFirma B", "data_quality": "calculated",
             "amount": "100", "unit": "t",
             "source": "pomiar", "process": "kalcynacja", "product": "wapno",
             "emission_tco2eq": "", "raport": "", "notes": ""},
        ],
    )

    # --- tbl_e_cons.csv ---
    _write_csv(os.path.join(folder, "tbl_e_cons.csv"),
        ["id", "year", "company", "data_quality", "amount", "unit", "source", "energy_source", "energy_type", "emission_tco2eq"],
        [
            # 450 MWh × 0.709 = 319.050 tCO2e
            {"id": 1, "year": 2025, "company": "TestFirma A", "data_quality": "measured",
             "amount": "450", "unit": "MWh",
             "source": "faktura", "energy_source": "Zakupiona", "energy_type": "Energia elektryczna nie OZE", "emission_tco2eq": ""},
            # 280 GJ ciepło × 0.292 = 81.760 tCO2e
            {"id": 2, "year": 2025, "company": "TestFirma A", "data_quality": "measured",
             "amount": "280", "unit": "GJ",
             "source": "faktura", "energy_source": "Zakupiona", "energy_type": "Energia cieplna", "emission_tco2eq": ""},
            # OZE → 0
            {"id": 3, "year": 2025, "company": "TestFirma A", "data_quality": "measured",
             "amount": "100", "unit": "MWh",
             "source": "PV", "energy_source": "Wyprodukowana", "energy_type": "Energia elektryczna z OZE", "emission_tco2eq": ""},
            # 2024 — do trendów
            {"id": 4, "year": 2024, "company": "TestFirma A", "data_quality": "",
             "amount": "500", "unit": "MWh",
             "source": "faktura", "energy_source": "Zakupiona", "energy_type": "Energia elektryczna nie OZE", "emission_tco2eq": ""},
        ],
    )

    # --- tbl_e_purc.csv (pusty, ale potrzebny) ---
    _write_csv(os.path.join(folder, "tbl_e_purc.csv"),
        ["id", "year", "company", "amount", "unit", "source", "energy_type", "trader", "factor", "emission_tco2eq"],
        [],
    )

    # --- tbl_authorisations.csv ---
    _write_csv(os.path.join(folder, "tbl_authorisations.csv"),
        ["id", "login", "company", "save", "read"],
        [
            {"id": 1, "login": "tester", "company": "TestFirma A", "save": "TRUE", "read": "TRUE"},
            {"id": 2, "login": "tester", "company": "TestFirma B", "save": "FALSE", "read": "TRUE"},
            {"id": 3, "login": "audytor", "company": "TestFirma A", "save": "FALSE", "read": "TRUE"},
            # Firma nieistniejąca → test spójności
            {"id": 4, "login": "tester", "company": "NieistniejącaFirma", "save": "TRUE", "read": "TRUE"},
        ],
    )

    # --- tbl_permissions.csv ---
    _write_csv(os.path.join(folder, "tbl_permissions.csv"),
        ["id", "login", "role"],
        [
            {"id": 1, "login": "admin1", "role": "admin"},
            {"id": 2, "login": "tester", "role": "użytkownik"},
        ],
    )

    # --- tbl_change_log.csv (pusty — audit log) ---
    _write_csv(os.path.join(folder, "tbl_change_log.csv"),
        ["id_rejestr_zmian", "login", "date_change", "table_name", "record_id",
         "change_type", "previous_data", "actual_data"],
        [],
    )

    return folder


@pytest.fixture
def uc(test_data_folder) -> EmissionUseCases:
    """Gotowy obiekt EmissionUseCases z testowymi danymi."""
    return EmissionUseCases(data_folder=test_data_folder)


@pytest.fixture
def repos(test_data_folder) -> RepositoryFactory:
    """Gotowy RepositoryFactory z testowymi danymi."""
    return RepositoryFactory(folder=test_data_folder)
