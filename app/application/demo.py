from decimal import Decimal
from app.infrastructure.repositories.file.repositories import RepositoryFactory
from app.application.use_cases import EmissionUseCases

def demo_01_companies():
    print("\n" + "═" * 65)
    print(" DEMO 1: Firmy i grupy kapitałowe")
    print("═" * 65)

    repos = RepositoryFactory("data_files")
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

    repos = RepositoryFactory("data_files")

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

    repos = RepositoryFactory("data_files")

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

    uc = EmissionUseCases("data_files")

    for company in ["GreenTech Polska", "NovaChem Industries", "EcoPartner Handel"]:
        # 1. Wywołujemy nasze nowe obliczenia dla danego roku i firmy
        print(f"\nUruchamiam silnik obliczeniowy dla: {company}...")
        uc.calculate_scope_1(year=2025, company=company)

        # 2. Wyświetlamy zaktualizowane podsumowanie
        uc.display_summary(year=2025, company=company)

def demo_06_validation():
    print("\n" + "═" * 65)
    print(" DEMO 6: Walidacja plików CSV")
    print("═" * 65)

    uc = EmissionUseCases("data_files")
    uc.validate_all_files()


def demo_07_display_tables():
    print("\n" + "═" * 65)
    print(" DEMO 7: Wyświetlanie tabel")
    print("═" * 65)

    uc = EmissionUseCases("data_files")

    print("\n─── Spalanie stacjonarne (NovaChem Industries) ───")
    uc.display_table("stationary", company="NovaChem Industries")

if __name__ == "__main__":
    demo_01_companies()
    demo_02_factors_and_converters()
    demo_03_emission_data()
    demo_05_summaries()
    demo_06_validation()
    demo_07_display_tables()

    print("\n" + "═" * 65)
    print(" Wszystkie demo zakończone pomyślnie!")
    print("═" * 65)