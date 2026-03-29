import sys
from decimal import Decimal
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from app.core.services.agent_esg_ai import EmissionAgent
from app.infrastructure.repositories.file.repositories import RepositoryFactory
from app.application.use_cases import EmissionUseCases

# Katalog data_files jest zawsze w korzeniu projektu (2 poziomy wyżej niż ten plik)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FOLDER = str(_PROJECT_ROOT / "data_files")

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def demo_01_companies():
    print("\n" + "═" * 65)
    print(" DEMO 1: Firmy i grupy kapitałowe")
    print("═" * 65)

    repos = RepositoryFactory(DATA_FOLDER)
    companies, errors = repos.companies.get_all()

    print(f"\nZaładowano {len(companies)} firm.")
    if errors:
        print(f"Błędy: {errors}")

    for group in repos.companies.get_groups():
        members = repos.companies.get_by_group(group)
        print(f"\n{group} ({len(members)} spółek)")
        for c in members:
            print(f"  [{c.co_id:>2}] {c.co_name:<30} {c.co_city}")

    firma = repos.companies.get_by_name("NovaChem Industries")
    if firma:
        print(f"\nZnaleziono: {firma.co_name} | NIP: {firma.co_nip} | {firma.co_city}")


def demo_02_factors_and_converters():
    print("\n" + "═" * 65)
    print(" DEMO 2: Wskaźniki i przeliczniki")
    print("═" * 65)

    repos = RepositoryFactory(DATA_FOLDER)

    factors, _ = repos.factors.get_all()
    print(f"\nZaładowano {len(factors)} wskaźników emisji:")
    for f in factors:
        print(f"  {f.factor_name:<30} {f.factor:>8} {f.unit_factor:<15} ({f.source})")

    el = repos.factors.get_factor("Energia elektryczna", "Polska")
    if el:
        print(f"\nWskaźnik dla en. elektrycznej: {el.factor} {el.unit_factor}")

    converters, _ = repos.converters.get_all()
    print(f"\nZaładowano {len(converters)} przeliczników:")
    for c in converters:
        print(f"  1 {c.unit_from} = {c.factor} {c.unit_to}")

    print("\nPrzykłady konwersji:")
    for val, uf, ut in [(Decimal("100"), "MWh", "GJ"), (Decimal("72"), "GJ", "MWh"),
                         (Decimal("5"), "t", "kg"), (Decimal("2000"), "l", "m3")]:
        try:
            result = repos.converters.convert(val, uf, ut)
            print(f"  {val} {uf} = {result} {ut}")
        except ValueError as e:
            print(f"  Błąd: {e}")


def demo_03_emission_data():
    print("\n" + "═" * 65)
    print(" DEMO 3: Dane emisyjne")
    print("═" * 65)

    repos = RepositoryFactory(DATA_FOLDER)

    stat, err = repos.stationary.get_all()
    print(f"\nSpalanie stacjonarne: {len(stat)} rekordów")
    if err:
        print(f"  Ostrzeżenia: {err}")

    nova = repos.stationary.get_filtered(company="NovaChem Industries")
    print(f"\n  NovaChem Industries — {len(nova)} instalacji:")
    for r in nova:
        print(f"    [{r.id:>2}] {r.fuel:<25} {r.amount:>8} {r.unit:<4} {r.installation}")

    mob, _ = repos.mobile.get_all()
    print(f"\nSpalanie mobilne: {len(mob)} rekordów")

    eco_transport = repos.mobile.get_filtered(company="EcoPartner Transport")
    print(f"  EcoPartner Transport — {len(eco_transport)} pojazdów:")
    for r in eco_transport:
        print(f"    [{r.id:>2}] {r.vehicle:<25} {r.fuel:<10} {r.amount:>8} {r.unit}")

    fug, _ = repos.fugitive.get_all()
    print(f"\nEmisje niezorganizowane: {len(fug)} rekordów")

def demo_05_summaries():
    print("\n" + "═" * 65)
    print(" DEMO 5: Podsumowania emisji")
    print("═" * 65)

    uc = EmissionUseCases(DATA_FOLDER)

    companies = ["GreenTech Polska", "NovaChem Industries", "EcoPartner Handel"]
    years = [2023, 2024, 2025, 2026]

    for company in companies:
        print(f"\nUruchamiam silnik obliczeniowy dla: {company}...")
        for year in years:
            uc.calculate_scope_1(year=year, company=company)

    for company in companies:
        for year in years:
            uc.display_summary(year=year, company=company)

def demo_06_validation():
    print("\n" + "═" * 65)
    print(" DEMO 6: Walidacja plików CSV")
    print("═" * 65)

    uc = EmissionUseCases(DATA_FOLDER)
    uc.validate_all_files()


def demo_07_display_tables():
    print("\n" + "═" * 65)
    print(" DEMO 7: Wyświetlanie tabel")
    print("═" * 65)

    uc = EmissionUseCases(DATA_FOLDER)

    print("\n─── Spalanie stacjonarne (NovaChem Industries) ───")
    uc.display_table("stationary", company="NovaChem Industries")

def demo_ai_assistant():
    load_dotenv()

    agent = EmissionAgent(api_key=getenv("GEMINI_API_KEY"))

    # Scenariusz 1: Interpretacja wyników
    print("Pytam agenta o analizę NovaChem...")
    agent.chat(
        company="NovaChem Industries",
        year=2025,
        user_query="Dlaczego moje emisje są tak wysokie i który obszar wymaga natychmiastowej redukcji?"
    )

    # Scenariusz 2: Pomoc w błędach danych
    print("Pytam agenta o błędy w GreenTech...")
    agent.chat(
        company="GreenTech Polska",
        year=2025,
        user_query="Dlaczego w raporcie mam zera przy spalaniu mobilnym, skoro wpisałem zużycie diesla? Daj odpowiedź w 2 zdaniach"
    )

if __name__ == "__main__":
    demo_01_companies()
    demo_02_factors_and_converters()
    demo_03_emission_data()
    demo_05_summaries()
    demo_06_validation()
    demo_07_display_tables()
    demo_ai_assistant()

    print("\n" + "═" * 65)
    print(" Wszystkie demo zakończone pomyślnie!")
    print("═" * 65)