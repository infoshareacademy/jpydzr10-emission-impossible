"""
Moduł komunikacji e-mail — wysyłanie zapytań do osób odpowiedzialnych za dane emisyjne.

Umożliwia:
- Rozwiązywanie odbiorców na podstawie uprawnień (save) i co_mail spółki
- Generowanie kontekstu rekordów (emisja deklarowana vs obliczona, odchylenie, średnia, r/r)
- Szablony wiadomości (weryfikacja, korekta, brak danych, odchylenie, dane źródłowe, własna)
- Wysyłanie przez SMTP (smtplib) lub tryb dry-run (zapis do pliku)
- Logowanie wysłanych wiadomości do tbl_email_log.csv
"""

import os
import smtplib
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from email.message import EmailMessage
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Analityk danych — Emission Impossible")
EMAIL_DRY_RUN = os.getenv("EMAIL_DRY_RUN", "true").lower() in ("true", "1", "tak")

TABLE_LABELS = {
    "stationary": "Spalanie stacjonarne",
    "mobile": "Spalanie mobilne",
    "process": "Emisje procesowe",
    "fugitive": "Emisje niezorganizowane",
    "energy_consumption": "Zużycie energii",
    "energy_purchased": "Zakupiona energia",
}
TEMPLATE_LABELS = {
    "weryfikacja": "Weryfikacja danych",
    "korekta": "Korekta danych",
    "brak_danych": "Brakujące dane",
    "odchylenie": "Wyjaśnienie odchylenia",
    "wlasna": "Własna wiadomość",
    "dane_zrodlowe": "Dane źródłowe",
}


def _round(d: Decimal) -> Decimal:
    """Zaokrągla Decimal do 3 miejsc po przecinku."""
    return d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def resolve_recipients(company: str, repos) -> list[str]:
    """Ustala listę adresów e-mail odbiorców dla danej spółki.

    Szuka:
    1. Użytkowników z save=TRUE dla spółki (login → email z tbl_users)
    2. co_mail ze spółki (koordynator / skrzynka funkcyjna)

    Zwraca deduplikowaną listę adresów e-mail.
    """
    emails = set()
    auths = repos.authorisations.get_filtered(company=company)
    save_logins = [a.login for a in auths if a.save]

    for login in save_logins:
        user = _get_user_by_login(login, repos)
        if user and user.email:
            emails.add(user.email)

    company_obj = repos.companies.get_by_name(company)
    if company_obj and company_obj.co_mail:
        emails.add(company_obj.co_mail)

    return sorted(emails)


def _get_user_by_login(login: str, repos) -> Optional[object]:
    """Pobiera dane użytkownika z tbl_users po loginie.

    Korzysta z UserManager — iteruje po załadowanych użytkownikach.
    """
    import app.application.users.user_manager as um
    for user in um.user_manager.users:
        if user.login == login:
            return user
    return None


def build_record_context(record, repo, repos, table_name: str) -> dict:
    """Buduje kontekst pojedynczego rekordu do wyświetlenia w mailu.

    Zawiera:
    - Dane rekordu (spółka, rok, paliwo/energia, ilość, jednostka)
    - Emisja deklarowana vs obliczona + odchylenie %
    - Średnia emisji z wszystkich lat dla tej spółki + tabeli
    - Porównanie do roku n-1
    """
    ctx = {
        "id": record.id,
        "company": record.company,
        "year": record.year,
        "amount": record.amount,
        "unit": record.unit,
    }

    if hasattr(record, "fuel"):
        ctx["detail_label"] = "Paliwo"
        ctx["detail_value"] = record.fuel
    if hasattr(record, "installation") and table_name in ("stationary", "fugitive"):
        ctx["installation"] = record.installation
    if hasattr(record, "vehicle"):
        ctx["detail_label"] = "Pojazd"
        ctx["detail_value"] = record.vehicle
        ctx["fuel"] = record.fuel
    if hasattr(record, "process"):
        ctx["detail_label"] = "Proces"
        ctx["detail_value"] = record.process
    if hasattr(record, "product") and table_name == "fugitive":
        ctx["detail_label"] = "Czynnik"
        ctx["detail_value"] = record.product
    if hasattr(record, "energy_type"):
        ctx["detail_label"] = "Typ energii"
        ctx["detail_value"] = record.energy_type
    if hasattr(record, "energy_source"):
        ctx["energy_source"] = record.energy_source

    declared = getattr(record, "emission_tco2eq", None)
    ctx["emission_declared"] = _round(declared) if declared else None

    calc = _calculate_record_emission(record, table_name, repos)
    ctx["emission_calculated"] = _round(calc) if calc > 0 else None

    if declared and calc > 0:
        diff = declared - calc
        pct = (diff / calc * 100).quantize(Decimal("0.1"))
        ctx["deviation_pct"] = f"+{pct}" if pct > 0 else str(pct)
    else:
        ctx["deviation_pct"] = None

    all_records = repo.get_filtered(company=record.company)
    emissions = []
    years_with_data = set()
    for r in all_records:
        em = getattr(r, "emission_tco2eq", None)
        if em and em > 0:
            emissions.append(em)
            years_with_data.add(r.year)
    if emissions:
        avg = sum(emissions) / len(emissions)
        ctx["avg_all_years"] = _round(avg)
        ctx["avg_years_range"] = sorted(years_with_data)
    else:
        ctx["avg_all_years"] = None
        ctx["avg_years_range"] = []

    prev_year = record.year - 1
    prev_records = [r for r in all_records if r.year == prev_year]
    if prev_records:
        prev_total = sum(r.emission_tco2eq for r in prev_records if r.emission_tco2eq and r.emission_tco2eq > 0)
        ctx["prev_year"] = prev_year
        ctx["prev_year_emission"] = _round(prev_total) if prev_total > 0 else None
    else:
        ctx["prev_year"] = prev_year
        ctx["prev_year_emission"] = None
    return ctx


def build_scope_context(company: str, year: int, scope: str, repos,
                        table_name: Optional[str] = None) -> dict:
    """Buduje kontekst zbiorczy dla spółki/zakresu/roku.

    scope: "1", "2", "1+2"
    table_name: opcjonalnie konkretna tabela (np. "stationary") — None = cały zakres
    """
    from app.application.use_cases import EmissionUseCases

    uc = EmissionUseCases.__new__(EmissionUseCases)
    uc.repos = repos

    ctx = {
        "company": company,
        "year": year,
        "scope": scope,
        "table_name": table_name,
        "table_label": TABLE_LABELS.get(table_name, table_name) if table_name else None,
    }
    summary_current = uc.generate_summary(year, year, company)
    summary_prev = uc.generate_summary(year - 1, year - 1, company)

    if scope == "1" and table_name:
        key_map = {
            "stationary": "scope1_stationary",
            "mobile": "scope1_mobile",
            "fugitive": "scope1_fugitive",
            "process": "scope1_process",
        }
        key = key_map.get(table_name, "")
        ctx["emission_current"] = summary_current.get(key, Decimal("0"))
        ctx["emission_prev"] = summary_prev.get(key, Decimal("0"))
    elif scope == "1":
        ctx["emission_current"] = (
            summary_current["scope1_stationary"] + summary_current["scope1_mobile"] +
            summary_current["scope1_fugitive"] + summary_current["scope1_process"]
        )
        ctx["emission_prev"] = (
            summary_prev["scope1_stationary"] + summary_prev["scope1_mobile"] +
            summary_prev["scope1_fugitive"] + summary_prev["scope1_process"]
        )
        ctx["breakdown"] = {
            "Spalanie stacjonarne": summary_current["scope1_stationary"],
            "Spalanie mobilne": summary_current["scope1_mobile"],
            "Emisje niezorganizowane": summary_current["scope1_fugitive"],
            "Emisje procesowe": summary_current["scope1_process"],
        }
    elif scope == "2":
        ctx["emission_current"] = summary_current["scope2_energy"]
        ctx["emission_prev"] = summary_prev["scope2_energy"]
    else:  # 1+2
        ctx["emission_current"] = summary_current["total"]
        ctx["emission_prev"] = summary_prev["total"]
        ctx["scope1_total"] = (
            summary_current["scope1_stationary"] + summary_current["scope1_mobile"] +
            summary_current["scope1_fugitive"] + summary_current["scope1_process"]
        )
        ctx["scope2_total"] = summary_current["scope2_energy"]

    if ctx["emission_prev"] > 0:
        diff = ctx["emission_current"] - ctx["emission_prev"]
        pct = (diff / ctx["emission_prev"] * 100).quantize(Decimal("0.1"))
        ctx["change_pct"] = f"+{pct}" if pct > 0 else str(pct)
    else:
        ctx["change_pct"] = None

    available_years = uc.get_available_years(company)
    years_with_data = []
    if available_years:
        totals = []
        for y in available_years:
            s = uc.generate_summary(y, y, company)
            if scope == "1":
                val = s["scope1_stationary"] + s["scope1_mobile"] + s["scope1_fugitive"] + s["scope1_process"]
            elif scope == "2":
                val = s["scope2_energy"]
            else:
                val = s["total"]
            if val > 0:
                totals.append(val)
                years_with_data.append(y)
        ctx["avg_all_years"] = _round(sum(totals) / len(totals)) if totals else None
    else:
        ctx["avg_all_years"] = None
    ctx["avg_years_range"] = years_with_data

    return ctx


def _calculate_record_emission(record, table_name: str, repos) -> Decimal:
    """Oblicza emisję rekordu na podstawie wskaźników (bez zapisu)."""
    from app.application.use_cases import EmissionUseCases
    uc = EmissionUseCases.__new__(EmissionUseCases)
    uc.repos = repos

    if table_name == "stationary":
        return uc._calculate_emission_for_record(record.amount, record.unit, record.fuel)
    elif table_name == "mobile":
        return uc._calculate_emission_for_record(record.amount, record.unit, record.fuel)
    elif table_name == "fugitive":
        return uc._calculate_emission_for_record(record.amount, record.unit, record.product)
    elif table_name == "process":
        return uc._calculate_emission_for_record(record.amount, record.unit, record.process)
    elif table_name == "energy_consumption":
        return uc._calculate_emission_for_record(record.amount, record.unit, record.energy_type)
    return Decimal("0")


def format_record_context(ctx: dict) -> str:
    """Formatuje kontekst rekordu do czytelnego tekstu (do maila i podglądu)."""
    lines = []
    detail = ""
    if "detail_label" in ctx:
        detail = f" | {ctx['detail_label']}: {ctx['detail_value']}"
    if "fuel" in ctx and ctx.get("detail_label") != "Paliwo":
        detail += f" | Paliwo: {ctx['fuel']}"

    lines.append(f"  Rekord #{ctx['id']}: {ctx['company']} | {ctx['year']}{detail} | {ctx['amount']} {ctx['unit']}")

    parts = []
    if ctx.get("emission_declared"):
        parts.append(f"Emisja deklarowana: {ctx['emission_declared']} tCO2e")
    if ctx.get("emission_calculated"):
        parts.append(f"Obliczona: {ctx['emission_calculated']} tCO2e")
    if parts:
        line = "  " + " | ".join(parts)
        if ctx.get("deviation_pct"):
            line += f" | Odchylenie: {ctx['deviation_pct']}%"
        lines.append(line)

    if ctx.get("avg_all_years"):
        years_range = ctx.get("avg_years_range", [])
        if years_range:
            years_info = f"{min(years_range)}-{max(years_range)}" if len(years_range) > 1 else str(years_range[0])
            lines.append(f"  Srednia z lat ({years_info}): {ctx['avg_all_years']} tCO2e")
        else:
            lines.append(f"  Srednia z lat: {ctx['avg_all_years']} tCO2e")
    if ctx.get("prev_year_emission"):
        lines.append(f"  Rok {ctx['prev_year']}: {ctx['prev_year_emission']} tCO2e")
    elif ctx.get("prev_year"):
        lines.append(f"  Rok {ctx['prev_year']}: brak danych")

    return "\n".join(lines)


def format_scope_context(ctx: dict) -> str:
    """Formatuje kontekst zbiorczy (spółka/zakres) do czytelnego tekstu."""
    lines = []
    scope_label = f"Scope {ctx['scope']}"
    table_info = f" — {ctx['table_label']}" if ctx.get("table_label") else ""
    lines.append(f"  {ctx['company']} | Rok {ctx['year']} | {scope_label}{table_info}")
    lines.append(f"  Emisja {ctx['year']}: {_round(ctx['emission_current'])} tCO2e")

    prev_year = ctx['year'] - 1
    if ctx['emission_prev'] > 0:
        lines.append(f"  Emisja {prev_year}: {_round(ctx['emission_prev'])} tCO2e")
        if ctx.get("change_pct"):
            lines.append(f"  Zmiana r/r: {ctx['change_pct']}%")
    else:
        lines.append(f"  Emisja {prev_year}: brak danych")

    if ctx.get("avg_all_years"):
        years_range = ctx.get("avg_years_range", [])
        if years_range:
            years_info = f"{min(years_range)}-{max(years_range)}" if len(years_range) > 1 else str(years_range[0])
            lines.append(f"  Srednia z lat ({years_info}): {ctx['avg_all_years']} tCO2e")
        else:
            lines.append(f"  Srednia z lat: {ctx['avg_all_years']} tCO2e")

    if ctx.get("breakdown"):
        lines.append("  Rozklad Scope 1:")
        for label, val in ctx["breakdown"].items():
            lines.append(f"    {label}: {_round(val)} tCO2e")

    if ctx.get("scope1_total") is not None:
        lines.append(f"  Scope 1: {_round(ctx['scope1_total'])} tCO2e")
        lines.append(f"  Scope 2: {_round(ctx['scope2_total'])} tCO2e")

    return "\n".join(lines)


def build_email_message(
    template_type: str,
    sender_name: str,
    recipients: list[str],
    company: str,
    context_text: str,
    custom_note: str = "",
    year: Optional[int] = None,
    table_label: Optional[str] = None,
) -> EmailMessage:
    """Buduje obiekt EmailMessage z szablonu i kontekstu."""

    subject_parts = ["[Emission Impossible]"]
    subject_parts.append(TEMPLATE_LABELS.get(template_type, template_type))
    subject_parts.append(f"— {company}")

    if year:
        subject_parts.append(f"({year})")
    subject = " ".join(subject_parts)
    body_lines = [
        "Szanowni Panstwo,",
        "",
    ]
    year_info = f" za rok {year}" if year else ""
    table_info = f" ({table_label})" if table_label else ""

    if template_type == "weryfikacja":
        body_lines.append(
            f"W ramach weryfikacji danych emisyjnych{year_info} zwracam sie "
            f"z prosba o potwierdzenie poprawnosci ponizszych danych{table_info}:"
        )
    elif template_type == "korekta":
        body_lines.append(
            f"W ramach weryfikacji danych emisyjnych{year_info} prosze "
            f"o korekte ponizszych danych{table_info}:"
        )
    elif template_type == "brak_danych":
        body_lines.append(
            f"W trakcie analizy danych emisyjnych{year_info} stwierdzono braki "
            f"w porownaniu do roku ubieglego{table_info}. Prosze o uzupelnienie:"
        )
    elif template_type == "odchylenie":
        body_lines.append(
            f"W ramach analizy danych emisyjnych{year_info} zwracam sie "
            f"z prosba o wyjasnienie ponizszych odchylen{table_info}:"
        )
    elif template_type == "dane_zrodlowe":
        body_lines.append(
            f"Prosze o przekazanie dokumentow zrodlowych potwierdzajacych "
            f"zuzycie/emisje{year_info}{table_info} dla ponizszych pozycji:"
        )
    elif template_type == "wlasna":
        body_lines.append(
            f"Zwracam sie w sprawie danych emisyjnych{year_info}{table_info}:"
        )

    body_lines.append("")
    body_lines.append(context_text)
    body_lines.append("")

    if custom_note:
        body_lines.append(custom_note)
        body_lines.append("")

    body_lines.extend([
        "Prosze o informacje zwrotna.",
        "",
        "Z powazaniem,",
        f"{sender_name}",
    ])

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>" if SMTP_USER else sender_name
    msg["To"] = "; ".join(recipients)
    msg.set_content("\n".join(body_lines))

    return msg


def send_email(msg: EmailMessage) -> tuple[bool, str]:
    """Wysyła wiadomość e-mail przez SMTP.

    W trybie dry-run (EMAIL_DRY_RUN=true) zapisuje do pliku zamiast wysyłać.
    Zwraca (sukces, komunikat).
    """
    if EMAIL_DRY_RUN:
        export_dir = os.path.join("data_files", "export")
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(export_dir, f"email_dry_run_{timestamp}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Do: {msg['To']}\n")
            f.write(f"Od: {msg['From']}\n")
            f.write(f"Temat: {msg['Subject']}\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write(msg.get_content())
        return True, f"[DRY RUN] Zapisano do: {filepath}"

    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Brak konfiguracji SMTP (SMTP_USER / SMTP_PASSWORD w .env)"

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True, "Wiadomosc wyslana pomyslnie"
    except smtplib.SMTPAuthenticationError:
        return False, "Blad uwierzytelniania SMTP — sprawdz SMTP_USER i SMTP_PASSWORD w .env"
    except smtplib.SMTPException as e:
        return False, f"Blad SMTP: {e}"
    except Exception as e:
        return False, f"Nieoczekiwany blad: {e}"


def preview_message(msg: EmailMessage) -> str:
    """Formatuje podgląd wiadomości do wyświetlenia w terminalu."""
    lines = [
        f"  Do: {msg['To']}",
        f"  Temat: {msg['Subject']}",
        "",
    ]
    content = msg.get_content()
    for line in content.strip().split("\n"):
        lines.append(f"  {line}")
    return "\n".join(lines)
