import sys
import os
import unicodedata
from os import getenv
from dotenv import load_dotenv

from app.application.use_cases import EmissionUseCases
from decimal import Decimal
from app.core.validators.input_validators import safe_input, safe_int, safe_decimal, safe_choice, safe_year_range, confirm
from app.application.class_models import MIN_YEAR, MAX_YEAR
from app.core.entities.charts import plot_companies_comparison, plot_pie_chart, plot_trend_chart
from app.application.pdf_export import export_summary_pdf, export_trend_pdf
from app.application.bulk_import import bulk_import, TABLE_MODELS
from app.application.email_sender import (
    resolve_recipients, build_record_context, build_scope_context,
    format_record_context, format_scope_context, build_email_message,
    send_email, preview_message, TABLE_LABELS, TEMPLATE_LABELS,
)
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
    "2": ("energy_purchased", "Zakupiona energia"),
    "3": ("energy_produced", "Wyprodukowana energia"),
    "4": ("energy_sold", "Sprzedana energia"),
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
    """Oblicza rzeczywistą szerokość tekstu w terminalu (emoji = 2 kolumny).

    Pomija variation selectors (U+FE0F, U+FE0E) i zero-width joiners (U+200D)
    które nie zajmują miejsca w terminalu.
    """
    w = 0
    for ch in text:
        cp = ord(ch)
        # Variation selectors i ZWJ — szerokość 0
        if cp in (0xFE0F, 0xFE0E, 0x200D):
            continue
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
    max_key_width = max((display_width(k) for k, _ in options if k != "-"), default=1)
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
            key_pad = ' ' * max(0, max_key_width - display_width(key))
            raw_text = f"  {key}{key_pad} │ {label}"
            colored_text = f"  {color}{key}{C.RESET}{key_pad} {C.DIM}│{C.RESET} {label}"
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
            ("2", "Dodaj uprawnienie"),
            ("3", "Edytuj uprawnienie"),
            ("4", "Usuń uprawnienie"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🔑")
        option = prompt()
        if option == '1':
            uc.display_table("authorisations")
            wait()
        elif option == '2':
            uc.add_authorisation_interactive()
            wait()
        elif option == '3':
            uc.display_table("authorisations")
            uc.edit_record_interactive("authorisations")
            wait()
        elif option == '4':
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
            ("2", "Dodaj rolę"),
            ("3", "Edytuj rolę"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="👑")
        option = prompt()
        if option == '1':
            uc.display_table("permissions")
            wait()
        elif option == '2':
            uc.add_permission_interactive()
            wait()
        elif option == '3':
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
            ("6", "🎯  Cele i symulacje"),
            ("7", "🔧  Narzędzia"),
            ("8", "👤  Użytkownicy"),
            ("9", "🤖  AI Asystent ESG"),
            ("10", "📧  Komunikacja e-mail"),
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
            menu_targets_simulations()
        elif option == '7':
            menu_tools()
        elif option == '8':
            menu_users()
        elif option == '9':
            menu_ai_agent()
        elif option == '10':
            menu_email()
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
        if confirm("Wyexportować raport do PDF? (tak/nie): "):
            try:
                path = export_summary_pdf(summary, company)
                success_msg(f"Raport PDF wyeksportowany: {path}")
            except Exception as e:
                error_msg(f"Błąd eksportu PDF: {e}")
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
            if confirm("Wyexportować trendy do PDF? (tak/nie): "):
                try:
                    path = export_trend_pdf(trends, company, year_from, year_to)
                    success_msg(f"Trendy PDF wyeksportowane: {path}")
                except Exception as e:
                    error_msg(f"Błąd eksportu PDF: {e}")
        wait()


def menu_companies():
    while True:
        cls()
        status_bar()
        print_menu("PRZEDSIĘBIORSTWO", [
            ("1", "Wyświetl firmy"),
            ("2", "Dodaj firmę"),
            ("3", "Edytuj firmę"),
            ("4", "Usuń firmę"),
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
            if not is_admin():
                error_msg("Dodawanie spółek wymaga uprawnień administratora.")
                wait()
                continue
            uc.add_company_interactive()
            wait()
        elif option == '3':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu.")
                wait()
                continue
            uc.display_companies(allowed_companies=save_companies)
            uc.edit_record_interactive("companies", allowed_companies=save_companies)
            wait()
        elif option == '4':
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
            ("2", "Dodaj wskaźnik"),
            ("3", "Edytuj wskaźnik"),
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
            if not is_admin():
                error_msg("Dodawanie wskaźników wymaga uprawnień administratora.")
                wait()
                continue
            uc.add_factor_interactive()
            wait()
        elif option == '3':
            if not require_login(): continue
            if not is_admin():
                error_msg("Edycja wskaźników wymaga uprawnień administratora.")
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
            ("2", "Dodaj przelicznik"),
            ("3", "Edytuj przelicznik"),
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
            if not is_admin():
                error_msg("Dodawanie przeliczników wymaga uprawnień administratora.")
                wait()
                continue
            uc.add_converter_interactive()
            wait()
        elif option == '3':
            if not require_login(): continue
            if not is_admin():
                error_msg("Edycja przeliczników wymaga uprawnień administratora.")
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
            ("2", "🛒  Zakupiona energia"),
            ("3", "☀️   Wyprodukowana energia"),
            ("4", "💸  Sprzedana energia"),
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
            elif repo_name == "energy_purchased":
                uc.add_energy_purchased_interactive(allowed_companies=save_companies)
            elif repo_name == "energy_produced":
                uc.add_energy_produced_interactive(allowed_companies=save_companies)
            elif repo_name == "energy_sold":
                uc.add_energy_sold_interactive(allowed_companies=save_companies)
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

def menu_targets_simulations():
    """Podmenu: cele redukcji emisji i symulacje what-if."""
    while True:
        cls()
        status_bar()
        print_menu("CELE I SYMULACJE", [
            ("1", "📊  Postęp redukcji vs cel"),
            ("2", "➕  Dodaj cel redukcji"),
            ("3", "🔮  Symulacja what-if"),
            ("4", "📋  Wyświetl cele"),
            ("5", "✏  Edytuj cel"),
            ("6", "🗑  Usuń cel"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="🎯")
        option = prompt()
        if option == '1':
            if not require_login(): continue
            company = choose_company()
            if company is None: continue
            uc.display_reduction_progress(company)
            wait()
        elif option == '2':
            if not require_login(): continue
            save_companies = get_save_companies()
            if not save_companies:
                error_msg("Brak uprawnień do zapisu.")
                wait()
                continue
            uc.add_reduction_target_interactive(allowed_companies=save_companies)
            wait()
        elif option == '3':
            if not require_login(): continue
            _simulation_interactive()
            wait()
        elif option == '4':
            if not require_login(): continue
            uc.display_table("reduction_targets")
            wait()
        elif option == '5':
            if not require_login(): continue
            uc.display_table("reduction_targets")
            uc.edit_record_interactive("reduction_targets")
            wait()
        elif option == '6':
            if not require_login(): continue
            uc.display_table("reduction_targets")
            uc.delete_record_interactive("reduction_targets")
            wait()
        elif option == '0':
            return
        else:
            error_msg()


def _simulation_interactive():
    """Interaktywna symulacja what-if."""
    company = choose_company()
    if company is None: return

    year = safe_int("Rok do symulacji: ", MIN_YEAR, MAX_YEAR)
    if year is None: return

    # Sprawdź czy są dane
    baseline = uc.generate_summary(year, year, company)
    if baseline["total"] <= 0:
        error_msg(f"Brak danych emisyjnych za rok {year} dla {company}.")
        return

    print(f"\n  Obecna emisja ({year}): {baseline['total']:.3f} tCO2e")
    print(f"\n  {C.CYAN}Dostępne scenariusze:{C.RESET}")
    print(f"    {C.YELLOW}1{C.RESET} {C.DIM}│{C.RESET} Przejście na OZE (% energii)")
    print(f"    {C.YELLOW}2{C.RESET} {C.DIM}│{C.RESET} Poprawa efektywności energetycznej")
    print(f"    {C.YELLOW}3{C.RESET} {C.DIM}│{C.RESET} Zmiana paliwa (np. węgiel → gaz)")
    print(f"    {C.YELLOW}4{C.RESET} {C.DIM}│{C.RESET} Własna redukcja (% Scope 1 i 2)")

    scenarios = []
    while True:
        choice = safe_input("\nScenariusz (numer lub 'ok' aby obliczyć): ")
        if choice is None: return
        if choice.lower() == "ok":
            break

        if choice == "1":
            pct = safe_decimal("Ile % energii nie-OZE zamienić na OZE? ", Decimal("1"), Decimal("100"))
            if pct is None: continue
            scenarios.append({"strategy": "oze_switch", "params": {"pct": pct}})
            info_msg(f"Dodano: przejście {pct}% energii na OZE")

        elif choice == "2":
            pct = safe_decimal("O ile % zmniejszyć zużycie? ", Decimal("1"), Decimal("100"))
            if pct is None: continue
            scenarios.append({"strategy": "efficiency", "params": {"pct": pct}})
            info_msg(f"Dodano: redukcja zużycia o {pct}%")

        elif choice == "3":
            from app.application.class_models import FUEL_TYPES
            from_fuel = safe_choice("Paliwo obecne: ", sorted(FUEL_TYPES))
            if from_fuel is None: continue
            to_fuel = safe_choice("Paliwo docelowe: ", sorted(FUEL_TYPES))
            if to_fuel is None: continue
            scenarios.append({"strategy": "fuel_switch", "params": {"from_fuel": from_fuel, "to_fuel": to_fuel}})
            info_msg(f"Dodano: zamiana {from_fuel} → {to_fuel}")

        elif choice == "4":
            s1 = safe_decimal("Redukcja Scope 1 (%): ", Decimal("0"), Decimal("100"))
            if s1 is None: continue
            s2 = safe_decimal("Redukcja Scope 2 (%): ", Decimal("0"), Decimal("100"))
            if s2 is None: continue
            scenarios.append({"strategy": "custom", "params": {"scope1_reduction_pct": s1, "scope2_reduction_pct": s2}})
            info_msg(f"Dodano: Scope 1 -{s1}%, Scope 2 -{s2}%")

        else:
            error_msg("Nieprawidłowy numer.")

    if not scenarios:
        error_msg("Nie dodano żadnych scenariuszy.")
        return

    result = uc.simulate_what_if(company, year, scenarios)
    uc.display_simulation_result(result)


def menu_tools():
    while True:
        cls()
        status_bar()
        print_menu("NARZĘDZIA", [
            ("1", "Walidacja plików CSV"),
            ("2", "Przeładuj dane"),
            ("3", "Weryfikacja wskaźników/przeliczeń"),
            ("4", "Walidacja spójności danych"),
            ("5", "Import danych z pliku (CSV/Excel)"),
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
        elif option == '5':
            if not require_login(): continue
            _bulk_import_interactive()
            wait()
        elif option == '0':
            return
        else:
            error_msg()


def _bulk_import_interactive():
    """Import hurtowy danych z pliku CSV lub Excel."""
    print(f"\n  {C.CYAN}Dostępne tabele docelowe:{C.RESET}")
    table_options = list(TABLE_MODELS.keys())
    for i, name in enumerate(table_options, 1):
        print(f"    {C.YELLOW}{i}{C.RESET} {C.DIM}│{C.RESET} {name}")

    raw = safe_input("Numer tabeli docelowej: ")
    if raw is None: return
    try:
        idx = int(raw)
        if not (1 <= idx <= len(table_options)):
            error_msg("Nieprawidłowy numer.")
            return
    except ValueError:
        error_msg("Podaj numer.")
        return

    repo_name = table_options[idx - 1]
    repo = getattr(uc.repos, repo_name, None)
    if repo is None:
        error_msg(f"Nie znaleziono repozytorium: {repo_name}")
        return

    file_path = safe_input("Ścieżka do pliku (CSV lub Excel): ")
    if file_path is None: return
    file_path = file_path.strip('"').strip("'")

    if not os.path.isfile(file_path):
        error_msg(f"Plik nie istnieje: {file_path}")
        return

    info_msg(f"Importuję z '{file_path}' do tabeli '{repo_name}'...")
    result = bulk_import(file_path, repo_name, repo)

    if result["imported"] > 0:
        success_msg(f"Zaimportowano: {result['imported']} rekordów")
    if result["skipped"] > 0:
        error_msg(f"Pominięto: {result['skipped']} wierszy z błędami")
    if result["errors"]:
        print(f"\n  {C.RED}Szczegóły błędów:{C.RESET}")
        for row_num, msg in result["errors"][:20]:
            print(f"    Wiersz {row_num}: {msg}")
        if len(result["errors"]) > 20:
            print(f"    ... i {len(result['errors']) - 20} więcej")


SCOPE1_TABLES = {
    "1": ("stationary", "Spalanie stacjonarne"),
    "2": ("mobile", "Spalanie mobilne"),
    "3": ("fugitive", "Emisje niezorganizowane"),
    "4": ("process", "Emisje procesowe"),
}

SCOPE2_TABLES = {
    "1": ("energy_consumption", "Zużycie energii"),
}

EMAIL_TEMPLATES = [
    ("1", "weryfikacja", "Weryfikacja danych"),
    ("2", "korekta", "Korekta danych"),
    ("3", "brak_danych", "Brakujące dane"),
    ("4", "odchylenie", "Wyjaśnienie odchylenia"),
    ("5", "dane_zrodlowe", "Dane źródłowe (dokumenty)"),
    ("6", "wlasna", "Własna wiadomość"),
]


def _choose_template() -> str | None:
    """Wyświetla menu szablonów i zwraca klucz wybranego szablonu lub None."""
    print(f"\n  {C.CYAN}Typ wiadomości:{C.RESET}")
    for key, _, label in EMAIL_TEMPLATES:
        print(f"    {C.YELLOW}{key}{C.RESET} {C.DIM}│{C.RESET} {label}")
    raw = safe_input("Wybierz typ: ")
    if raw is None:
        return None
    for key, template_key, _ in EMAIL_TEMPLATES:
        if raw == key:
            return template_key
    error_msg("Nieprawidłowy wybór.")
    return None


def _choose_email_table() -> tuple[str, str] | None:
    """Wybór tabeli emisyjnej — dostępne wszystkie tabele Scope 1 i 2."""
    all_tables = {
        "1": ("stationary", "Spalanie stacjonarne"),
        "2": ("mobile", "Spalanie mobilne"),
        "3": ("fugitive", "Emisje niezorganizowane"),
        "4": ("process", "Emisje procesowe"),
        "5": ("energy_consumption", "Zużycie energii"),
    }
    print(f"\n  {C.CYAN}Wybierz tabelę:{C.RESET}")
    for key, (_, label) in all_tables.items():
        print(f"    {C.YELLOW}{key}{C.RESET} {C.DIM}│{C.RESET} {label}")
    raw = safe_input("Numer tabeli: ")
    if raw is None or raw not in all_tables:
        error_msg("Nieprawidłowy wybór.")
        return None
    return all_tables[raw]


def _confirm_and_send_email(msg, sender_login, recipients, company, template_type,
                            table_name=None, record_ids=None, scope=None, year=None):
    """Podgląd, potwierdzenie i wysyłka maila + logowanie."""
    print(f"\n  {C.CYAN}{'═' * 55}{C.RESET}")
    print(f"  {C.BOLD}PODGLĄD WIADOMOŚCI{C.RESET}")
    print(f"  {C.CYAN}{'═' * 55}{C.RESET}")
    print(preview_message(msg))
    print(f"  {C.CYAN}{'═' * 55}{C.RESET}")

    if not confirm("\n  Wyślij? "):
        info_msg("Anulowano wysyłkę.")
        return

    ok, result_msg = send_email(msg)
    if ok:
        success_msg(result_msg)
        uc.log_sent_email(
            sender=sender_login,
            recipients=recipients,
            company=company,
            template_type=template_type,
            subject=msg["Subject"],
            table_name=table_name,
            record_ids=record_ids,
            scope=scope,
            year=year,
        )
    else:
        error_msg(result_msg)


def menu_email():
    """Główne podmenu komunikacji e-mail."""
    while True:
        cls()
        status_bar()
        print_menu("KOMUNIKACJA E-MAIL", [
            ("1", "Wskaż spółkę (zakres/tabela)"),
            ("2", "Wskaż konkretne ID rekordów"),
            ("-", ""),
            ("3", "Historia wysłanych wiadomości"),
            ("-", ""),
            ("0", "Powrót"),
        ], icon="📧")
        option = prompt()
        if option == '1':
            if not require_login():
                continue
            _email_by_company()
            wait()
        elif option == '2':
            if not require_login():
                continue
            _email_by_record_ids()
            wait()
        elif option == '3':
            if not require_login():
                continue
            _email_history()
            wait()
        elif option == '0':
            return
        else:
            error_msg()


def _email_by_company():
    """Opcja [1] — Wskaż spółkę → podmenu zakresu → mail do osób z save + koordynator."""
    company = choose_company()
    if company is None:
        return

    recipients = resolve_recipients(company, uc.repos)
    if not recipients:
        error_msg(f"Brak odbiorców dla spółki: {company}")
        return
    info_msg(f"Odbiorcy: {', '.join(recipients)}")
    print(f"\n  {C.CYAN}Zakres zapytania:{C.RESET}")
    print(f"    {C.YELLOW}1{C.RESET} {C.DIM}│{C.RESET} Scope 1 (emisje bezpośrednie)")
    print(f"    {C.YELLOW}2{C.RESET} {C.DIM}│{C.RESET} Scope 2 (energia)")
    print(f"    {C.YELLOW}3{C.RESET} {C.DIM}│{C.RESET} Całkowity ślad węglowy (Scope 1+2)")
    scope_choice = safe_input("Wybierz zakres: ")
    if scope_choice is None:
        return

    scope = None
    table_name = None
    table_label = None

    if scope_choice == "1":
        scope = "1"
        print(f"\n  {C.CYAN}Scope 1 — szczegóły:{C.RESET}")
        for key, (_, label) in SCOPE1_TABLES.items():
            print(f"    {C.YELLOW}{key}{C.RESET} {C.DIM}│{C.RESET} {label}")
        print(f"    {C.YELLOW}5{C.RESET} {C.DIM}│{C.RESET} Cały Scope 1")
        sub = safe_input("Wybierz: ")
        if sub is None:
            return
        if sub in SCOPE1_TABLES:
            table_name, table_label = SCOPE1_TABLES[sub]
        elif sub == "5":
            table_name = None  # cały Scope 1
            table_label = None
        else:
            error_msg("Nieprawidłowy wybór.")
            return

    elif scope_choice == "2":
        scope = "2"
        table_name = None
        table_label = None

    elif scope_choice == "3":
        scope = "1+2"
        table_name = None
        table_label = None
    else:
        error_msg("Nieprawidłowy wybór.")
        return

    available_years = uc.get_available_years(company)
    if available_years:
        print(f"\n  {C.DIM}Dostępne lata: {', '.join(str(y) for y in available_years)}{C.RESET}")
    year = safe_int("Rok: ", MIN_YEAR, MAX_YEAR)
    if year is None:
        return

    ctx = build_scope_context(company, year, scope, uc.repos, table_name)
    context_text = format_scope_context(ctx)
    print(f"\n  {C.CYAN}Dane do zapytania:{C.RESET}")
    print(context_text)

    template_type = _choose_template()
    if template_type is None:
        return
    
    custom_note = safe_input("Dodatkowa uwaga (Enter = pomiń): ", allow_empty=True) or ""
    sender_user = None
    for u in user_manager.user_manager.users:
        if u.login == current_user:
            sender_user = u
            break
    sender_name = f"{sender_user.name} {sender_user.surname}" if sender_user else current_user
    msg = build_email_message(
        template_type=template_type,
        sender_name=sender_name,
        recipients=recipients,
        company=company,
        context_text=context_text,
        custom_note=custom_note,
        year=year,
        table_label=table_label or TABLE_LABELS.get(table_name, f"Scope {scope}"),
    )

    _confirm_and_send_email(
        msg, current_user, recipients, company, template_type,
        table_name=table_name, scope=scope, year=year,
    )


def _email_by_record_ids():
    """Opcja [2] — Wskaż konkretne ID rekordów → mail do osób z save dla spółki rekordu."""
    table_result = _choose_email_table()
    if table_result is None:
        return
    table_name, table_label = table_result
    repo = uc.get_repo_by_table_name(table_name)
    if repo is None:
        error_msg(f"Nieznana tabela: {table_name}")
        return

    # Wyświetl dostępne rekordy dla zalogowanego użytkownika
    allowed = get_read_companies()
    print(f"\n  {C.CYAN}Dostępne rekordy ({table_label}):{C.RESET}")
    uc.display_table(table_name, allowed_companies=allowed)

    raw_ids = safe_input("\nID rekordów (rozdzielone przecinkiem, np. 1,5,12): ")
    if raw_ids is None:
        return

    try:
        record_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]
    except ValueError:
        error_msg("Nieprawidłowe ID — podaj liczby rozdzielone przecinkiem.")
        return

    if not record_ids:
        error_msg("Nie podano żadnych ID.")
        return

    records = []
    companies_in_query = set()
    for rid in record_ids:
        ok, result = uc.check_record_access(rid, table_name, current_user)
        if not ok:
            error_msg(result)
            return
        record = repo.get_by_id(rid)
        records.append(record)
        companies_in_query.add(record.company)

    context_parts = []
    for record in records:
        ctx = build_record_context(record, repo, uc.repos, table_name)
        context_parts.append(format_record_context(ctx))

    context_text = "\n\n".join(context_parts)
    print(f"\n  {C.CYAN}Dane do zapytania:{C.RESET}")
    print(context_text)
    all_recipients = set()
    for comp in companies_in_query:
        all_recipients.update(resolve_recipients(comp, uc.repos))
    recipients = sorted(all_recipients)

    if not recipients:
        error_msg("Brak odbiorców dla wskazanych spółek.")
        return
    info_msg(f"Odbiorcy: {', '.join(recipients)}")
    template_type = _choose_template()
    if template_type is None:
        return

    custom_note = safe_input("Dodatkowa uwaga (Enter = pomiń): ", allow_empty=True) or ""
    sender_user = None
    for u in user_manager.user_manager.users:
        if u.login == current_user:
            sender_user = u
            break
    sender_name = f"{sender_user.name} {sender_user.surname}" if sender_user else current_user
    company_label = ", ".join(sorted(companies_in_query))
    msg = build_email_message(
        template_type=template_type,
        sender_name=sender_name,
        recipients=recipients,
        company=company_label,
        context_text=context_text,
        custom_note=custom_note,
        year=records[0].year if records else None,
        table_label=table_label,
    )

    _confirm_and_send_email(
        msg, current_user, recipients, company_label, template_type,
        table_name=table_name, record_ids=record_ids, year=records[0].year if records else None,
    )


def _email_history():
    """Wyświetla historię wysłanych wiadomości."""
    logs, errors = uc.repos.email_log.get_all()
    if not logs:
        info_msg("Brak wysłanych wiadomości.")
        return

    if not uc.is_admin(current_user):
        logs = [l for l in logs if l.sender == current_user]

    if not logs:
        info_msg("Brak Twoich wiadomości.")
        return

    print(f"\n  {C.CYAN}Historia wysłanych wiadomości ({len(logs)}):{C.RESET}\n")
    for log in logs[-20:]:  # ostatnie 20
        date_str = log.date.strftime("%Y-%m-%d %H:%M") if hasattr(log.date, 'strftime') else str(log.date)
        template = TEMPLATE_LABELS.get(log.template_type, log.template_type)
        print(f"  {C.DIM}[{date_str}]{C.RESET} {C.YELLOW}{template}{C.RESET}")
        print(f"    {log.company} | Do: {log.recipients}")
        if log.record_ids:
            print(f"    ID: {log.record_ids} ({log.table_name})")
        print()


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
