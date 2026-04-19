import sys
import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Callable

def safe_input(prompt: str, allow_empty: bool = False, max_length: int = 200) -> Optional[str]:
    while True:
        try:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            raw_bytes = sys.stdin.buffer.readline()
            value = raw_bytes.decode("utf-8", errors="replace").rstrip("\n").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if value.lower() == "q":
            return None
        if not value and not allow_empty:
            print("Wartość nie może być pusta. Wpisz 'q' aby anulować.")
            continue
        if len(value) > max_length:
            print(f"Za długie (max {max_length} znaków).")
            continue
        return value

def safe_int(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    while True:
        raw = safe_input(prompt)
        if raw is None:
            return None
        try:
            value = int(raw)
        except ValueError:
            print(f"'{raw}' nie jest liczbą całkowitą.")
            continue
        if min_val is not None and value < min_val:
            print(f"Minimum: {min_val}")
            continue
        if max_val is not None and value > max_val:
            print(f"Maksimum: {max_val}")
            continue
        return value


def safe_decimal(prompt: str, min_val: Optional[Decimal] = None, max_val: Optional[Decimal] = None) -> Optional[Decimal]:
    while True:
        raw = safe_input(prompt)
        if raw is None:
            return None
        raw = raw.replace(",", ".")  # polska konwencja
        try:
            value = Decimal(raw)
        except InvalidOperation:
            print(f"'{raw}' nie jest prawidłową liczbą.")
            continue
        if min_val is not None and value < min_val:
            print(f"Minimum: {min_val}")
            continue
        if max_val is not None and value > max_val:
            print(f"Maksimum: {max_val}")
            continue
        return value


def safe_choice(prompt: str, choices: list[str], case_sensitive: bool = False) -> Optional[str]:
    while True:
        print(f"  Dostępne: {', '.join(choices)}")
        raw = safe_input(prompt)
        if raw is None:
            return None
        if case_sensitive:
            if raw in choices:
                return raw
        else:
            for choice in choices:
                if raw.lower() == choice.lower():
                    return choice
        print(f"'{raw}' nie jest na liście.")


def safe_bool(prompt: str) -> Optional[bool]:
    while True:
        raw = safe_input(prompt)
        if raw is None:
            return None
        if raw.lower() in ("t", "tak", "y", "yes", "1", "true"):
            return True
        if raw.lower() in ("n", "nie", "no", "0", "false"):
            return False
        print("Wpisz 'tak' lub 'nie'.")


def safe_year_range(prompt: str, min_val: int = 1990, max_val: int = 2100,
                    allow_all: bool = True) -> Optional[tuple[int, int]]:
    """Pobiera rok lub zakres lat (np. '2025' lub '2019-2025').
    Enter = wszystkie lata (min_val–max_val) jeśli allow_all=True.
    Zwraca (rok_od, rok_do) lub None (anulowanie)."""
    while True:
        raw = safe_input(prompt, allow_empty=allow_all)
        if raw is None:
            return None
        raw = raw.strip()
        if raw == "" and allow_all:
            return (min_val, max_val)
        if "-" in raw:
            parts = raw.split("-", 1)
            try:
                year_from = int(parts[0].strip())
                year_to = int(parts[1].strip())
            except ValueError:
                print(f"Nieprawidłowy format. Wpisz rok (np. 2025) lub zakres (np. 2019-2025).")
                continue
            if year_from > year_to:
                print(f"Rok początkowy ({year_from}) nie może być większy niż końcowy ({year_to}).")
                continue
        else:
            try:
                year_from = year_to = int(raw)
            except ValueError:
                print(f"'{raw}' nie jest liczbą. Wpisz rok (np. 2025) lub zakres (np. 2019-2025).")
                continue
        if year_from < min_val or year_to > max_val:
            print(f"Zakres lat musi mieścić się w {min_val}–{max_val}.")
            continue
        return (year_from, year_to)


def confirm(prompt: str = "Czy na pewno? (tak/nie): ") -> bool:
    result = safe_bool(prompt)
    return result is True


def safe_input_validated(
    prompt: str,
    validator: Callable[[str], Optional[str]],
    allow_empty: bool = False,
) -> Optional[str]:
    """Pobiera dane od użytkownika i waliduje je funkcją validator.

    validator(value) zwraca:
    - None      → wartość poprawna, akceptuj
    - str       → komunikat błędu, powtórz pytanie

    Wpisanie 'q' anuluje i zwraca None.
    """
    while True:
        value = safe_input(prompt, allow_empty=allow_empty)
        if value is None:
            return None
        error = validator(value)
        if error is None:
            return value
        print(f"  ✗ {error}")


# ---------------------------------------------------------------------------
# Gotowe validatory dla typowych pól spółki
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
_PHONE_RE = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")


def validate_email(v: str) -> Optional[str]:
    """Zwraca None jeśli OK, komunikat błędu jeśli niepoprawny."""
    return None if _EMAIL_RE.match(v.strip()) else f"Nieprawidłowy e-mail: '{v}'. Przykład: firma@domena.pl"


def validate_phone(v: str) -> Optional[str]:
    return None if _PHONE_RE.match(v.strip()) else f"Nieprawidłowy telefon: '{v}'. Przykład: +48 22 123 45 67"


def validate_nip(v: str) -> Optional[str]:
    digits = re.sub(r"[\s\-]", "", v.strip())
    if not digits.isdigit() or len(digits) != 10:
        return f"NIP musi mieć dokładnie 10 cyfr (podano: '{v}')"
    return None


def validate_regon(v: str) -> Optional[str]:
    digits = re.sub(r"[\s\-]", "", v.strip())
    if not digits.isdigit() or len(digits) not in (9, 14):
        return f"REGON musi mieć 9 lub 14 cyfr (podano: '{v}')"
    return None


def validate_krs(v: str) -> Optional[str]:
    digits = re.sub(r"[\s\-]", "", v.strip())
    if not digits.isdigit() or len(digits) != 10:
        return f"KRS musi mieć dokładnie 10 cyfr (podano: '{v}')"
    return None