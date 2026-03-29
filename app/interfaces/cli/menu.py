import sys
import os
import unicodedata
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
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    GREEN   = "\033[32m"
    CYAN    = "\033[36m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    WHITE   = "\033[97m"

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def status_bar():
    if current_user:
        companies = uc.get_user_companies(current_user)
        print(f"  {C.DIM}Zalogowano:{C.RESET} {C.GREEN}{current_user}{C.RESET}"
              f"  {C.DIM}│{C.RESET}  "
              f"{C.DIM}Dostęp:{C.RESET} {C.CYAN}{len(companies)} spółek{C.RESET}")
    else:
        print(f"  {C.DIM}Niezalogowany{C.RESET}")
    print()

def display_width(text: str) -> int:
    """Oblicza rzeczywistą szerokość tekstu w terminalu (emoji = 2 kolumny)."""
    w = 0
    for ch in text:
        cat = unicodedata.east_asian_width(ch)
        if cat in ('W', 'F'):
            w += 2
        else:
            w += 1
    return w


def pad_to(text: str, target: int) -> str:
    """Dopełnia tekst spacjami do docelowej szerokości terminalowej."""
    current = display_width(text)
    return text + ' ' * max(0, target - current)


def center_to(text: str, target: int) -> str:
    """Centruje tekst z uwzględnieniem szerokości emoji."""
    current = display_width(text)
    total_pad = max(0, target - current)
    left = total_pad // 2
    right = total_pad - left
    return ' ' * left + text + ' ' * right


def print_menu(title, options, width=42, icon=""):
    if icon:
        title = f"{icon}  {title}"
    inner = width - 2
    print(f"  {C.CYAN}╔{'═' * inner}╗{C.RESET}")
    centered_title = center_to(title, inner)
    print(f"  {C.CYAN}║{C.BOLD}{C.WHITE}{centered_title}{C.RESET}{C.CYAN}║{C.RESET}")
    print(f"  {C.CYAN}╠{'═' * inner}╣{C.RESET}")
    for key, label in options:
        if key == "-":
            print(f"  {C.CYAN}╟{'─' * inner}╢{C.RESET}")
        else:
            color = C.DIM if key == "0" else C.YELLOW
            raw_text = f"  {key} │ {label}"
            colored_text = f"  {color}{key}{C.RESET} {C.DIM}│{C.RESET} {label}"
            padding = ' ' * max(0, inner - display_width(raw_text))
            print(f"  {C.CYAN}║{C.RESET}{colored_text}{padding}{C.CYAN}║{C.RESET}")
    print(f"  {C.CYAN}╚{'═' * inner}╝{C.RESET}")


def prompt():
    return input(f"\n  {C.CYAN}▶{C.RESET} Wybierz opcję: ")


def error_msg(msg="Wprowadzono zły parametr!"):
    print(f"  {C.RED}✗ {msg}{C.RESET}")


def success_msg(msg):
    print(f"  {C.GREEN}✓ {msg}{C.RESET}")


def info_msg(msg):
    print(f"  {C.BLUE}ℹ {msg}{C.RESET}")


def wait():
    input(f"\n  {C.DIM}Enter aby kontynuować...{C.RESET}")


LOGO = f"""
  {C.CYAN}{C.BOLD}
   ███████╗███╗   ███╗██╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
   ██╔════╝████╗ ████║██║██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
   █████╗  ██╔████╔██║██║███████╗███████╗██║██║   ██║██╔██╗ ██║
   ██╔══╝  ██║╚██╔╝██║██║╚════██║╚════██║██║██║   ██║██║╚██╗██║
   ███████╗██║ ╚═╝ ██║██║███████║███████║██║╚██████╔╝██║ ╚████║
   ╚══════╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
        {C.GREEN}I M P O S S I B L E{C.RESET}
  {C.DIM}─────────────────────────────────────────────────────────{C.RESET}
  {C.DIM}  Kalkulator śladu węglowego  │  v1.0{C.RESET}
"""

def choose_company(allow_all: bool = False):
    """Wyświetla listę firm użytkownika do wyboru. Zwraca nazwę firmy lub None."""
    if current_user:
        companies = uc.get_user_companies(current_user)
    else:
        companies = []

    if companies:
        print(f"\n  {C.CYAN}Twoje spółki:{C.RESET}")
        for i, name in enumerate(companies, 1):
            print(f"    {C.YELLOW}{i}{C.RESET} {C.DIM}│{C.RESET} {name}")
        print(f"    {C.DIM}0 │ Wpisz ręcznie{C.RESET}")
        if allow_all:
            print(f"    {C.DIM}Enter = wszystkie{C.RESET}")
        choice = input(f"\n  {C.CYAN}▶{C.RESET} Wybierz numer lub 'q' aby anulować: ").strip()
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
        error_msg("Nieprawidłowy wybór.")
        return None
    else:
        if allow_all:
            return safe_input("Firma (Enter = wszystkie): ", allow_empty=True) or None
        return safe_input("Firma: ")

def menu_users():
    while True:
        cls()
        status_bar()
        print_menu("UŻYTKOWNICY", [
            ("1", "Login"),
            ("2", "Utwórz nowego użytkownika"),
            ("3", "Edytuj dane"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="👤")
        option = prompt()
        if option == "1":
            global current_user
            user = user_manager.user_prompt()
            if user:
                current_user = user.login
                companies = uc.get_user_companies(current_user)
                success_msg(f"Zalogowano jako: {current_user}")
                info_msg(f"Dostęp do spółek: {', '.join(companies) if companies else 'brak'}")
            wait()
        elif option == "2":
            user_manager.create_user()
            wait()
        elif option == "3":
            user_manager.edit_user()
            wait()
        elif option == "0":
            return
        else:
            error_msg()

def menu_0():
    global current_user
    while True:
        cls()
        print(LOGO)
        if current_user:
            print(f"  {C.GREEN}Witaj, {current_user}!{C.RESET}\n")
            print_menu("EMISSION IMPOSSIBLE", [
                ("1", "Przejdź do aplikacji"),
                ("2", "Zmień użytkownika"),
                ("-", ""),
                ("0", "Zakończ"),
            ], icon="🌍")
        else:
            print_menu("EMISSION IMPOSSIBLE", [
                ("1", "Zaloguj się"),
                ("2", "Utwórz konto"),
                ("-", ""),
                ("0", "Zakończ"),
            ], icon="🌍")
        option = prompt()
        if option == '1':
            if current_user:
                return menu_1()
            else:
                user = user_manager.user_prompt()
                if user:
                    current_user = user.login
                    companies = uc.get_user_companies(current_user)
                    success_msg(f"Zalogowano jako: {current_user}")
                    info_msg(f"Dostęp do spółek: {', '.join(companies) if companies else 'brak'}")
                    wait()
                    return menu_1()
                else:
                    error_msg("Nieprawidłowy login lub hasło.")
                    wait()
        elif option == '2':
            if current_user:
                current_user = None
                info_msg("Wylogowano.")
                wait()
            else:
                user_manager.create_user()
                wait()
        elif option == '0':
            cls()
            print(f"\n  {C.GREEN}Do widzenia! 👋{C.RESET}\n")
            sys.exit()
        else:
            error_msg()

def menu_1():
    while True:
        cls()
        status_bar()
        print_menu("MENU GŁÓWNE", [
            ("1", "📊  Podsumowanie"),
            ("2", "🏢  Przedsiębiorstwo"),
            ("3", "📈  Wskaźniki emisji"),
            ("4", "🔄  Przeliczniki"),
            ("5", "🔥  Dane emisyjne"),
            ("6", "📋  Obliczenia i raporty"),
            ("7", "🔧  Narzędzia"),
            ("8", "👤  Użytkownicy"),
            ("9", "🤖  AI Asystent ESG"),
            ("-", ""),
            ("0", "Zakończ"),
        ], icon="☰")
        option = prompt()
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
            error_msg()

def menu_summary():
    while True:
        cls()
        status_bar()
        print_menu("PODSUMOWANIE", [
            ("1", "Moje spółki (zbiorczo)"),
            ("2", "Wybrana firma"),
            ("-", ""),
            ("3", "Oblicz Scope 1 (zbiorczo)"),
            ("4", "Oblicz Scope 1 (wybrana)"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📊")
        option = prompt()
        if option == '1':
            if not current_user:
                error_msg("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
                wait()
                continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            uc.display_summary_for_user(current_user, year)
            wait()
        elif option == '2':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            uc.display_summary(year, company)
            wait()
        elif option == '3':
            if not current_user:
                error_msg("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
                wait()
                continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            country = safe_input("Kraj (domyślnie Polska): ", allow_empty=True) or "Polska"
            companies = uc.get_user_companies(current_user)
            for comp in companies:
                uc.calculate_scope_1(year, comp, country)
            uc.display_summary_for_user(current_user, year)
            wait()
        elif option == '4':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            country = safe_input("Kraj (domyślnie Polska): ", allow_empty=True) or "Polska"
            uc.calculate_scope_1(year, company, country)
            uc.display_summary(year, company)
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_companies():
    while True:
        cls()
        status_bar()
        print_menu("PRZEDSIĘBIORSTWO", [
            ("1", "Wyświetl firmy"),
            ("2", "Edytuj firmę"),
            ("3", "Usuń firmę"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🏢")
        option = prompt()
        if option == '1':
            uc.display_companies()
            wait()
        elif option == '2':
            uc.edit_record_interactive("companies")
            wait()
        elif option == '3':
            uc.delete_record_interactive("companies")
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_factors():
    while True:
        cls()
        status_bar()
        print_menu("WSKAŹNIKI EMISJI", [
            ("1", "Wyświetl wskaźniki"),
            ("2", "Edytuj wskaźnik"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📈")
        option = prompt()
        if option == '1':
            uc.display_table("factors")
            wait()
        elif option == '2':
            uc.edit_record_interactive("factors")
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_converters():
    while True:
        cls()
        status_bar()
        print_menu("PRZELICZNIKI", [
            ("1", "Wyświetl przeliczniki"),
            ("2", "Edytuj przelicznik"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🔄")
        option = prompt()
        if option == '1':
            uc.display_table("converters")
            wait()
        elif option == '2':
            uc.edit_record_interactive("converters")
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_emission_data():
    while True:
        cls()
        status_bar()
        print_menu("DANE EMISYJNE", [
            ("1", "🔥  Spalanie stacjonarne"),
            ("2", "🚗  Spalanie mobilne"),
            ("3", "🏭  Emisje procesowe"),
            ("4", "💨  Emisje niezorganizowane"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📁")
        option = prompt()
        if option in REPO_NAMES:
            repo_name, label = REPO_NAMES[option]
            menu_emission_crud(repo_name, label)
        elif option == '0':
            return
        else:
            error_msg()

def menu_emission_crud(repo_name: str, label: str):
    while True:
        cls()
        status_bar()
        print_menu(label.upper(), [
            ("1", "Wyświetl"),
            ("2", "Dodaj"),
            ("3", "Edytuj"),
            ("4", "Usuń"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📝")
        option = prompt()
        if option == '1':
            raw_year = safe_input("Rok (Enter = wszystkie): ", allow_empty=True)
            year = int(raw_year) if raw_year else None
            company = choose_company(allow_all=True)
            uc.display_table(repo_name, year=year, company=company)
            wait()
        elif option == '2':
            if repo_name == "stationary":
                uc.add_stationary_interactive()
            elif repo_name == "mobile":
                uc.add_mobile_interactive()
            else:
                info_msg("Dodawanie dla tej kategorii nie jest jeszcze zaimplementowane.")
            wait()
        elif option == '3':
            uc.edit_record_interactive(repo_name)
            wait()
        elif option == '4':
            uc.delete_record_interactive(repo_name)
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_reports():
    while True:
        cls()
        status_bar()
        print_menu("OBLICZENIA I RAPORTY", [
            ("1", "Oblicz Scope 1"),
            ("2", "Podsumowanie emisji"),
            ("3", "Oblicz i pokaż raport"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📋")
        option = prompt()
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
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_tools():
    while True:
        cls()
        status_bar()
        print_menu("NARZĘDZIA", [
            ("1", "Walidacja plików CSV"),
            ("2", "Przeładuj dane"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🔧")
        option = prompt()
        if option == '1':
            uc.validate_all_files()
            wait()
        elif option == '2':
            uc.repos.reload_all()
            success_msg("Dane przeładowane.")
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_ai_agent():
    try:
        from app.core.services.agent_esg_ai import EmissionAgent
    except ImportError:
        error_msg("Moduł AI nie jest dostępny. Sprawdź instalację zależności.")
        return

    api_key = getenv("GEMINI_API_KEY")
    if not api_key:
        error_msg("Brak klucza GEMINI_API_KEY w zmiennych środowiskowych.")
        return

    agent = EmissionAgent(api_key=api_key)

    while True:
        cls()
        status_bar()
        print_menu("AI ASYSTENT ESG", [
            ("1", "Zadaj pytanie o emisje"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🤖")
        option = prompt()
        if option == '1':
            company = choose_company()
            if company is None: continue
            year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
            if year is None: continue
            query = safe_input("Twoje pytanie: ")
            if query is None: continue
            agent.chat(company=company, year=year, user_query=query)
            wait()
        elif option == '0':
            return
        else:
            error_msg()
