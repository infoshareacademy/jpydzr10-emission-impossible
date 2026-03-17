from decimal import Decimal, InvalidOperation
from typing import Optional

def safe_input(prompt: str, allow_empty: bool = False, max_length: int = 200) -> Optional[str]:
    while True:
        try:
            value = input(prompt).strip()
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


def confirm(prompt: str = "Czy na pewno? (tak/nie): ") -> bool:
    result = safe_bool(prompt)
    return result is True