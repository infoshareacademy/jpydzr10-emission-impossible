import sys
from os import getenv
from dotenv import load_dotenv

from app.application.use_cases import EmissionUseCases
from app.core.validators.input_validators import safe_input, safe_int, safe_choice, confirm
from app.application.class_models import MIN_YEAR, MAX_YEAR
import app.application.users.user_manager as user_manager

load_dotenv()

uc = EmissionUseCases("data_files")
current_user = None

REPO_NAMES = {
    "1": ("stationary", "Spalanie stacjonarne"),
    "2": ("mobile", "Spalanie mobilne"),
    "3": ("process", "Emisje procesowe"),
    "4": ("fugitive", "Emisje niezorganizowane"),
}

def choose_company(allow_all: bool = False):
    """Wyświetla listę firm użytkownika do wyboru. Zwraca nazwę firmy lub None.
    allow_all=True: Enter oznacza 'wszystkie' (zwraca None bez anulowania)."""
    if current_user:
        companies = uc.get_user_companies(current_user)
    else:
        companies = []

    if companies:
        print("\nTwoje spółki:")
        for i, name in enumerate(companies, 1):
            print(f"  {i}. {name}")
        print(f"  0. Wpisz ręcznie")
        if allow_all:
            print(f"  Enter = wszystkie")
        choice = input("Wybierz numer lub 'q' aby anulować: ").strip()
        if choice.lower() == 'q':
            return None
        if choice == '' and allow_all:
            return None
        if choice == '0':
            return safe_input("Firma: ", allow_empty=allow_all) or None
        try:
            idx = int(choice)
            if 1 <= idx <= len(companies):
                return companies[idx - 1]
        except ValueError:
            pass
        print("Nieprawidłowy wybór.")
        return None
    else:
        if allow_all:
            return safe_input("Firma (Enter = wszystkie): ", allow_empty=True) or None
        return safe_input("Firma: ")

def menu_users():
    while True:
        print(
            "┌────────── UŻYTKOWNICY ──────────┐\n"
            "| 1 - Login                       |\n"
            "| 2 - Utwórz nowego użytkownika   |\n"
            "| 3 - Edytuj dane                 |\n"
            "| 0 - Powrót                      |\n"
            "└─────────────────────────────────┘")
        option = input("Wybierz opcję: ")
        if option == "1":
            global current_user
            user = user_manager.user_prompt()
            if user:
                current_user = user.login
                companies = uc.get_user_companies(current_user)
                print(f"Zalogowano jako: {current_user}")
                print(f"Dostęp do spółek: {', '.join(companies) if companies else 'brak'}")
        elif option == "2":
            user_manager.create_user()
        elif option == "3":
            user_manager.edit_user()
        elif option == "0":
            return
        else:
            print("Wprowadzono zły parametr!")


def menu_0():
    while True:
        print("┌────── EMISSION IMPOSSIBLE ──────┐\n"
              "| 1 - Wczytaj projekt             |\n"
              "| 2 - Nowy projekt                |\n"
              "| 0 - Zakończ                     |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            return menu_1()
        elif option == '2':
            return menu_1()
        elif option == '0':
            print("Do widzenia!")
            sys.exit()
        else:
            print('Wprowadzono zły parametr!')


def menu_1():
    while True:
        print("┌──────── MENU GŁÓWNE ────────────┐\n"
              "| 1 - Podsumowanie                |\n"
              "| 2 - Przedsiębiorstwo            |\n"
              "| 3 - Wskaźniki emisji            |\n"
              "| 4 - Przeliczniki                |\n"
              "| 5 - Dane emisyjne               |\n"
              "| 6 - Obliczenia i raporty        |\n"
              "| 7 - Narzędzia                   |\n"
              "| 8 - Użytkownicy                 |\n"
              "| 9 - AI Asystent ESG             |\n"
              "| 0 - Zakończ                     |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            menu_summary()
        elif option == '2':
            menu_companies()
        elif option == '3':
            menu_factors()
        elif option == '4':
            menu_converters()
        elif option == '5':
            menu_emission_data()
        elif option == '6':
            menu_reports()
        elif option == '7':
            menu_tools()
        elif option == '8':
            menu_users()
        elif option == '9':
            menu_ai_agent()
        elif option == '0':
            return menu_0()
        else:
            print('Wprowadzono zły parametr!')

def menu_summary():
    while True:
        user_info = f" ({current_user})" if current_user else ""
        print(f"┌──────── PODSUMOWANIE{user_info:>11} ───┐\n"
              "| 1 - Moje spółki (zbiorczo)              |\n"
              "| 2 - Wybrana firma                       |\n"
              "| 3 - Oblicz Scope 1 (zbiorczo)           |\n"
              "| 4 - Oblicz Scope 1 (wybrana)            |\n"
              "| 0 - Powrót                              |\n"
              "└─────────────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            if not current_user:
                print("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
                continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            uc.display_summary_for_user(current_user, year)
        elif option == '2':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            uc.display_summary(year, company)
        elif option == '3':
            if not current_user:
                print("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
                continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            country = safe_input("Kraj (domyślnie Polska): ", allow_empty=True) or "Polska"
            companies = uc.get_user_companies(current_user)
            for comp in companies:
                uc.calculate_scope_1(year, comp, country)
            uc.display_summary_for_user(current_user, year)
        elif option == '4':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            country = safe_input("Kraj (domyślnie Polska): ", allow_empty=True) or "Polska"
            uc.calculate_scope_1(year, company, country)
            uc.display_summary(year, company)
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_companies():
    while True:
        print("╔════════ PRZEDSIĘBIORSTWO ═══════╗\n"
              "║ 1 - Wyświetl firmy              ║\n"
              "║ 2 - Edytuj firmę                ║\n"
              "║ 3 - Usuń firmę                  ║\n"
              "║ 0 - Powrót                      ║\n"
              "╚═════════════════════════════════╝")
        option = input('Wybierz opcję: ')
        if option == '1':
            uc.display_companies()
        elif option == '2':
            uc.edit_record_interactive("companies")
        elif option == '3':
            uc.delete_record_interactive("companies")
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_factors():
    while True:
        print("┌─────── WSKAŹNIKI EMISJI ────────┐\n"
              "| 1 - Wyświetl wskaźniki          |\n"
              "| 2 - Edytuj wskaźnik             |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            uc.display_table("factors")
        elif option == '2':
            uc.edit_record_interactive("factors")
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_converters():
    while True:
        print("┌──────── PRZELICZNIKI ───────────┐\n"
              "| 1 - Wyświetl przeliczniki       |\n"
              "| 2 - Edytuj przelicznik          |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            uc.display_table("converters")
        elif option == '2':
            uc.edit_record_interactive("converters")
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_emission_data():
    while True:
        print("┌───────── DANE EMISYJNE ─────────┐\n"
              "| 1 - Spalanie stacjonarne        |\n"
              "| 2 - Spalanie mobilne            |\n"
              "| 3 - Emisje procesowe            |\n"
              "| 4 - Emisje niezorganizowane     |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option in REPO_NAMES:
            repo_name, label = REPO_NAMES[option]
            menu_emission_crud(repo_name, label)
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')


def menu_emission_crud(repo_name: str, label: str):
    while True:
        print(f"┌──── {label.upper():^26} ────┐\n"
              f"| 1 - Wyświetl                    |\n"
              f"| 2 - Dodaj                       |\n"
              f"| 3 - Edytuj                      |\n"
              f"| 4 - Usuń                        |\n"
              f"| 0 - Powrót                      |\n"
              f"└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            year = safe_int("Rok (Enter = wszystkie): ", MIN_YEAR, MAX_YEAR, allow_empty=True)
            print("Firma (Enter = wszystkie):")
            company = choose_company(allow_all=True)
            uc.display_table(repo_name, year=year, company=company)
        elif option == '2':
            if repo_name == "stationary":
                uc.add_stationary_interactive()
            elif repo_name == "mobile":
                uc.add_mobile_interactive()
            else:
                print("Dodawanie dla tej kategorii nie jest jeszcze zaimplementowane.")
        elif option == '3':
            uc.edit_record_interactive(repo_name)
        elif option == '4':
            uc.delete_record_interactive(repo_name)
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_reports():
    while True:
        print("┌───── OBLICZENIA I RAPORTY ──────┐\n"
              "| 1 - Oblicz Scope 1              |\n"
              "| 2 - Podsumowanie emisji         |\n"
              "| 3 - Oblicz i pokaż raport       |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option in ('1', '2', '3'):
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue

            if option == '1':
                uc.calculate_scope_1(year, company)
            elif option == '2':
                uc.display_summary(year, company)
            elif option == '3':
                uc.calculate_scope_1(year, company)
                uc.display_summary(year, company)
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_tools():
    while True:
        print("┌─────────── NARZĘDZIA ───────────┐\n"
              "| 1 - Walidacja plików CSV        |\n"
              "| 2 - Przeładuj dane              |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            uc.validate_all_files()
        elif option == '2':
            uc.repos.reload_all()
            print("Dane przeładowane.")
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')

def menu_ai_agent():
    try:
        from app.core.services.agent_esg_ai import EmissionAgent
    except ImportError:
        print("Moduł AI nie jest dostępny. Sprawdź instalację zależności.")
        return

    api_key = getenv("GEMINI_API_KEY")
    if not api_key:
        print("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych.")
        return

    agent = EmissionAgent(api_key=api_key)

    while True:
        print("┌──────── AI ASYSTENT ESG ────────┐\n"
              "| 1 - Zadaj pytanie o emisje      |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            query = safe_input("Twoje pytanie: ")
            if query is None: continue
            agent.chat(company=company, year=year, user_query=query)
        elif option == '0':
            return
        else:
            print('Wprowadzono zły parametr!')
