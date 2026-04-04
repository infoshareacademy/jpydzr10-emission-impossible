import sys
import os
import unicodedata
from os import getenv
from dotenv import load_dotenv

from app.application.use_cases import EmissionUseCases
from app.core.validators.input_validators import safe_input, safe_int, safe_choice, safe_year_range, confirm
from app.application.class_models import MIN_YEAR, MAX_YEAR
from app.core.entities.charts import plot_companies_comparison, plot_pie_chart, plot_trend_chart
import app.application.users.user_manager as user_manager

load_dotenv()

uc = EmissionUseCases("data_files")
current_user = None

SCOPE1_REPOS = {
    "1": ("stationary", "Spalanie stacjonarne"),
    "2": ("mobile", "Spalanie mobilne"),
    "3": ("process", "Emisje procesowe"),
    "4": ("fugitive", "Emisje niezorganizowane"),
}

SCOPE2_REPOS = {
    "1": ("energy_consumption", "Zużycie energii"),
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

def is_admin() -> bool:
    """Sprawdza czy zalogowany użytkownik jest adminem."""
    if not current_user:
        return False
    return uc.is_admin(current_user)


def status_bar():
    if current_user:
        companies = uc.get_user_companies(current_user)
        role = uc.get_user_role(current_user)
        role_color = C.RED if role == "admin" else C.BLUE
        print(f"  {C.DIM}Zalogowano:{C.RESET} {C.GREEN}{current_user}{C.RESET}"
              f"  {C.DIM}│{C.RESET}  "
              f"{C.DIM}Rola:{C.RESET} {role_color}{role}{C.RESET}"
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


def require_login() -> bool:
    """Sprawdza czy użytkownik jest zalogowany. Wyświetla błąd jeśli nie."""
    if not current_user:
        error_msg("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
        wait()
        return False
    return True


def get_read_companies() -> list[str]:
    """Zwraca listę spółek do których zalogowany użytkownik ma uprawnienia odczytu."""
    if not current_user:
        return []
    return uc.get_user_companies(current_user, read_only=True)


def get_save_companies() -> list[str]:
    """Zwraca listę spółek do których zalogowany użytkownik ma uprawnienia zapisu."""
    if not current_user:
        return []
    return uc.get_user_companies(current_user, read_only=False)


def check_save_permission(company: str) -> bool:
    """Sprawdza czy zalogowany użytkownik ma uprawnienia zapisu dla danej spółki."""
    save_companies = get_save_companies()
    if company not in save_companies:
        error_msg(f"Brak uprawnień do zapisu dla: {company}")
        return False
    return True


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
        options = [
            ("1", "Utwórz nowego użytkownika"),
            ("2", "Edytuj dane użytkownika"),
        ]
        if is_admin():
            options.append(("-", ""))
            options.append(("3", "Zarządzaj uprawnieniami spółek"))
            options.append(("4", "Zarządzaj rolami użytkowników"))
        options.append(("-", ""))
        options.append(("0", "Powrót"))
        print_menu("UŻYTKOWNICY", options, icon="👤")
        option = prompt()
        if option == "1":
            user_manager.create_user()
            wait()
        elif option == "2":
            user_manager.edit_user()
            wait()
        elif option == "3" and is_admin():
            menu_admin_authorisations()
        elif option == "4" and is_admin():
            menu_admin_permissions()
        elif option == "0":
            return
        else:
            error_msg()


def menu_admin_authorisations():
    """Podmenu admina — zarządzanie uprawnieniami spółek (tbl_authorisations)."""
    while True:
        cls()
        status_bar()
        print_menu("UPRAWNIENIA SPÓŁEK", [
            ("1", "Wyświetl uprawnienia"),
            ("2", "Edytuj uprawnienie"),
            ("3", "Usuń uprawnienie"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🔑")
        option = prompt()
        if option == '1':
            uc.display_table("authorisations")
            wait()
        elif option == '2':
            uc.display_table("authorisations")
            uc.edit_record_interactive("authorisations")
            wait()
        elif option == '3':
            uc.display_table("authorisations")
            uc.delete_record_interactive("authorisations")
            wait()
        elif option == '0':
            return
        else:
            error_msg()


def menu_admin_permissions():
    """Podmenu admina — zarządzanie rolami użytkowników (tbl_permissions)."""
    while True:
        cls()
        status_bar()
        print_menu("ROLE UŻYTKOWNIKÓW", [
            ("1", "Wyświetl role"),
            ("2", "Edytuj rolę"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="👑")
        option = prompt()
        if option == '1':
            uc.display_table("permissions")
            wait()
        elif option == '2':
            uc.display_table("permissions")
            uc.edit_record_interactive("permissions")
            wait()
        elif option == '0':
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
                    # Włącz audit log (trigger) — od teraz zmiany będą rejestrowane
                    uc.repos.set_audit_context(current_user)
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
            ("1", "📋  Raporty"),
            ("2", "🏢  Przedsiębiorstwo"),
            ("3", "📈  Wskaźniki emisji"),
            ("4", "🔄  Przeliczniki"),
            ("5", "🔥  Dane emisyjne"),
            ("6", "🔧  Narzędzia"),
            ("7", "👤  Użytkownicy"),
            ("8", "🤖  AI Asystent ESG"),
            ("-", ""),
            ("0", "Zakończ"),
        ], icon="☰")
        option = prompt()
        if option == '1':
            menu_reports()
        elif option == '2':
            menu_companies()
        elif option == '3':
            menu_factors()
        elif option == '4':
            menu_converters()
        elif option == '5':
            menu_emission_data()
        elif option == '6':
            menu_tools()
        elif option == '7':
            menu_users()
        elif option == '8':
            menu_ai_agent()
        elif option == '0':
            return menu_0()
        else:
            error_msg()

def _reports_whole_organization():
    """Raport dla całej organizacji (wszystkie spółki zalogowanego użytkownika)."""
    if not current_user:
        error_msg("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
        wait()
        return
    year_range = safe_year_range("Rok lub zakres (np. 2025 lub 2019-2025, Enter = wszystkie): ", MIN_YEAR, MAX_YEAR)
    if year_range is None: return
    year_from, year_to = year_range
    companies = uc.get_user_companies(current_user)
    uc.display_summary_for_user(current_user, year_from, year_to)
    summaries = [uc.generate_summary(year_from, year_to, c) for c in companies]
    has_data = any(s["total"] > 0 for s in summaries)
    if has_data:
        if confirm("Wyświetlić wykres porównawczy? (tak/nie): "):
            try:
                plot_companies_comparison(summaries, year_from)
            except Exception as e:
                error_msg(f"Nie można wyświetlić wykresu: {e}")
        if confirm("Wyexportować raport do CSV? (tak/nie): "):
            try:
                uc.export_summary_csv(summaries, f"raport_organizacja_{year_from}-{year_to}.csv")
                success_msg("Raport CSV wyeksportowany do data_files/export/")
            except Exception as e:
                error_msg(f"Błąd eksportu: {e}")
    wait()


def _reports_single_company():
    """Raport dla pojedynczej spółki — obliczenia + podsumowanie."""
    if not current_user:
        error_msg("Musisz się najpierw zalogować (Menu → Użytkownicy → Login).")
        wait()
        return
    company = choose_company()
    if company is None: return
    year_range = safe_year_range("Rok lub zakres (np. 2025 lub 2019-2025, Enter = wszystkie): ", MIN_YEAR, MAX_YEAR)
    if year_range is None: return
    year_from, year_to = year_range
    uc.display_summary(year_from, year_to, company)
    summary = uc.generate_summary(year_from, year_to, company)
    if summary["total"] > 0:
        if confirm("Wyświetlić wykres kołowy? (tak/nie): "):
            try:
                plot_pie_chart(summary, year_from)
            except Exception as e:
                error_msg(f"Nie można wyświetlić wykresu: {e}")
        if confirm("Wyexportować raport do CSV? (tak/nie): "):
            try:
                safe_name = company.replace(" ", "_").replace(".", "")
                uc.export_summary_csv([summary], f"raport_{safe_name}_{year_from}-{year_to}.csv")
                success_msg("Raport CSV wyeksportowany do data_files/export/")
            except Exception as e:
                error_msg(f"Błąd eksportu: {e}")
    wait()

def _reports_trends():
    """Raport trendów rok do roku — spółka lub cała organizacja."""
    if not require_login(): return
    print_menu("TRENDY ROK DO ROKU", [
        ("1", "Cała organizacja"),
        ("2", "Pojedyncza spółka"),
        ("-", ""),
        ("0", "Powrót"),
    ], icon="📊")
    option = prompt()
    if option == '1':
        year_range = safe_year_range("Zakres lat (np. 2023-2025): ", MIN_YEAR, MAX_YEAR, allow_all=False)
        if year_range is None: return
        year_from, year_to = year_range
        if year_from == year_to:
            error_msg("Trendy wymagają zakresu co najmniej 2 lat (np. 2023-2025).")
            wait()
            return
        rows = uc.display_trend_report_organization(current_user, year_from, year_to)
        if rows and confirm("Wyexportować trendy do CSV? (tak/nie): "):
            try:
                # Konwertuj do formatu trend
                trend_rows = []
                for r in rows:
                    trend_rows.append({
                        "year": r["year"], "company": "ORGANIZACJA",
                        "scope1_stationary": "", "scope1_mobile": "",
                        "scope1_fugitive": "", "scope1_process": "",
                        "scope1_total": r["scope1"], "scope2_energy": r["scope2"],
                        "total": r["total"], "change_pct": None,
                    })
                uc.export_trend_csv(trend_rows, f"trendy_organizacja_{year_from}-{year_to}.csv")
                success_msg("Trendy CSV wyeksportowane do data_files/export/")
            except Exception as e:
                error_msg(f"Błąd eksportu: {e}")
        wait()
    elif option == '2':
        company = choose_company()
        if company is None: return
        year_range = safe_year_range("Zakres lat (np. 2023-2025): ", MIN_YEAR, MAX_YEAR, allow_all=False)
        if year_range is None: return
        year_from, year_to = year_range
        if year_from == year_to:
            error_msg("Trendy wymagają zakresu co najmniej 2 lat (np. 2023-2025).")
            wait()
            return
        trends = uc.display_trend_report(company, year_from, year_to)
        if trends:
            if confirm("Wyświetlić wykres trendów? (tak/nie): "):
                try:
                    plot_trend_chart(trends, company)
                except Exception as e:
                    error_msg(f"Nie można wyświetlić wykresu: {e}")
            if confirm("Wyexportować trendy do CSV? (tak/nie): "):
                try:
                    safe_name = company.replace(" ", "_").replace(".", "")
                    uc.export_trend_csv(trends, f"trendy_{safe_name}_{year_from}-{year_to}.csv")
                    success_msg("Trendy CSV wyeksportowane do data_files/export/")
                except Exception as e:
                    error_msg(f"Błąd eksportu: {e}")
        wait()


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
            if not require_login(): continue
            uc.display_companies(allowed_companies=get_read_companies())
            wait()
        elif option == '2':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu.")
                wait()
                continue
            uc.display_companies(allowed_companies=save_companies)
            uc.edit_record_interactive("companies", allowed_companies=save_companies)
            wait()
        elif option == '3':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu.")
                wait()
                continue
            uc.display_companies(allowed_companies=save_companies)
            uc.delete_record_interactive("companies", allowed_companies=save_companies)
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
            if not require_login(): continue
            uc.display_table("factors")
            wait()
        elif option == '2':
            if not require_login(): continue
            if not get_save_companies():
                error_msg("Brak uprawnień do edycji.")
                wait()
                continue
            uc.display_table("factors")
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
            if not require_login(): continue
            uc.display_table("converters")
            wait()
        elif option == '2':
            if not require_login(): continue
            if not get_save_companies():
                error_msg("Brak uprawnień do edycji.")
                wait()
                continue
            uc.display_table("converters")
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
        if not current_user:
            error_msg("Musisz się najpierw zalogować aby przeglądać dane emisyjne.")
            wait()
            return
        print_menu("DANE EMISYJNE", [
            ("1", "🔥  Scope 1 — emisje bezpośrednie"),
            ("2", "⚡  Scope 2 — energia pośrednia"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📁")
        option = prompt()
        if option == '1':
            menu_scope1_data()
        elif option == '2':
            menu_scope2_data()
        elif option == '0':
            return
        else:
            error_msg()


def menu_scope1_data():
    while True:
        cls()
        status_bar()
        print_menu("SCOPE 1 — EMISJE BEZPOŚREDNIE", [
            ("1", "🔥  Spalanie stacjonarne"),
            ("2", "🚗  Spalanie mobilne"),
            ("3", "🏭  Emisje procesowe"),
            ("4", "💨  Emisje niezorganizowane"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🔥", width=46)
        option = prompt()
        if option in SCOPE1_REPOS:
            repo_name, label = SCOPE1_REPOS[option]
            menu_emission_crud(repo_name, label)
        elif option == '0':
            return
        else:
            error_msg()


def menu_scope2_data():
    while True:
        cls()
        status_bar()
        print_menu("SCOPE 2 — ENERGIA POŚREDNIA", [
            ("1", "⚡  Zużycie energii"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="⚡", width=46)
        option = prompt()
        if option in SCOPE2_REPOS:
            repo_name, label = SCOPE2_REPOS[option]
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
            if not require_login(): continue
            raw_year = safe_input("Rok (Enter = wszystkie): ", allow_empty=True)
            year = int(raw_year) if raw_year else None
            company = choose_company(allow_all=True)
            # Filtruj po spółkach użytkownika gdy nie wybrano konkretnej
            allowed = get_read_companies() if company is None else None
            uc.display_table(repo_name, year=year, company=company, allowed_companies=allowed)
            wait()
        elif option == '2':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu w żadnej spółce.")
                wait()
                continue
            if repo_name == "stationary":
                uc.add_stationary_interactive(allowed_companies=save_companies)
            elif repo_name == "mobile":
                uc.add_mobile_interactive(allowed_companies=save_companies)
            elif repo_name == "process":
                uc.add_process_interactive(allowed_companies=save_companies)
            elif repo_name == "fugitive":
                uc.add_fugitive_interactive(allowed_companies=save_companies)
            elif repo_name == "energy_consumption":
                uc.add_energy_consumption_interactive(allowed_companies=save_companies)
            wait()
        elif option == '3':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu w żadnej spółce.")
                wait()
                continue
            uc.display_table(repo_name, allowed_companies=save_companies)
            uc.edit_record_interactive(repo_name, allowed_companies=save_companies)
            wait()
        elif option == '4':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu w żadnej spółce.")
                wait()
                continue
            uc.display_table(repo_name, allowed_companies=save_companies)
            uc.delete_record_interactive(repo_name, allowed_companies=save_companies)
            wait()
        elif option == '0':
            return
        else:
            error_msg()

def menu_reports():
    while True:
        cls()
        status_bar()
        print_menu("RAPORTY", [
            ("1", "Cała organizacja"),
            ("2", "Pojedyncza spółka"),
            ("3", "Trendy rok do roku"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📋")
        option = prompt()
        if option == '1':
            _reports_whole_organization()
        elif option == '2':
            _reports_single_company()
        elif option == '3':
            _reports_trends()
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
            ("3", "Weryfikacja wskaźników i przeliczeń"),
            ("4", "Walidacja spójności danych"),
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
        elif option == '3':
            country = safe_input("Kraj (domyślnie Polska): ", allow_empty=True) or "Polska"
            uc.display_verification_report(country)
            wait()
        elif option == '4':
            uc.display_data_consistency_report()
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
            if not require_login(): continue
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
