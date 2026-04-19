import csv
import os
import re
from getpass import getpass
from dataclasses import dataclass
from dotenv import load_dotenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

# Load variables from .env in project root
load_dotenv()

FOLDER_PATH = "data_files"
USERS_FILE = os.getenv("USERS_FILE", "tbl_users.csv")
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "1234")

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@dataclass
class User:
    name: str
    surname: str
    email: str
    phone_number: str
    login: str
    password: str

class UserManager:
    def __init__(self):
        self.file_path = os.path.join(FOLDER_PATH, USERS_FILE)
        self.users = self._load_users()

    def _load_users(self):
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [User(**row) for row in reader]

    def _save_users(self):
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=User.__dataclass_fields__.keys())
            writer.writeheader()
            for user in self.users:
                writer.writerow(user.__dict__)

    def add_user(self, name, surname, email, phone_number, login, password):
        if not all([name, surname, email, phone_number, login, password]):
            print("Wszystkie pola są wymagane.")
            return None
        if not re.match(EMAIL_REGEX, email):
            print("Nieprawidłowy format e-mail.")
            return None
        if any(u.login == login for u in self.users):
            print(f"Login '{login}' już istnieje.")
            return None

        hashed = ph.hash(password)
        new_user = User(name, surname, email, phone_number, login, hashed)
        self.users.append(new_user)
        self._save_users()
        print(f"Użytkownik '{login}' został dodany.")
        return new_user

    def authenticate_user(self, login, password):
        for user in self.users:
            if user.login == login:
                try:
                    if ph.verify(user.password, password):
                        if ph.check_needs_rehash(user.password):
                            user.password = ph.hash(password)
                            self._save_users()
                        return user
                except VerifyMismatchError:
                    return None
        return None

    def edit_user(self, login, field, new_value):
        for user in self.users:
            if user.login == login:
                if not new_value:
                    print("Wartość nie może być pusta.")
                    return False
                if field == "email" and not re.match(EMAIL_REGEX, new_value):
                    print("Nieprawidłowy format e-mail.")
                    return False
                if hasattr(user, field):
                    if field == "password":
                        new_value = ph.hash(new_value)
                    setattr(user, field, new_value)
                    self._save_users()
                    print(f"Zaktualizowano pole '{field}' dla użytkownika '{login}'.")
                    return True
                else:
                    print(f"Pole '{field}' nie istnieje.")
                    return False
        print(f"Nie znaleziono użytkownika '{login}'.")
        return False

    def list_users(self):
        print("\nLista użytkowników:")
        for u in self.users:
            print(f"  {u.login} — {u.name} {u.surname}")
        print()

user_manager = UserManager()

def user_prompt():
    login = input("Login: ")
    password = getpass("Hasło: ")
    user = user_manager.authenticate_user(login, password)
    if user:
        print(f"Witaj {user.name} {user.surname}!")
        return user
    else:
        return None

EDITABLE_FIELDS = {
    "1": ("name", "Imię"),
    "2": ("surname", "Nazwisko"),
    "3": ("email", "E-mail"),
    "4": ("phone_number", "Numer telefonu"),
    "5": ("login", "Login"),
    "6": ("password", "Hasło"),
}

def create_user():
    print("\n─── Tworzenie nowego użytkownika ───")
    print("(Wpisz 'q' aby anulować)\n")
    name = input("Imię: ")
    if name.lower() == 'q': return
    surname = input("Nazwisko: ")
    if surname.lower() == 'q': return
    email = input("E-mail: ")
    if email.lower() == 'q': return
    phone_number = input("Numer telefonu: ")
    if phone_number.lower() == 'q': return
    login = input("Login: ")
    if login.lower() == 'q': return
    password = getpass("Hasło: ")
    if password.lower() == 'q': return
    user_manager.add_user(name, surname, email, phone_number, login, password)

def edit_user():
    print("\n─── Edycja danych użytkownika ───\n")
    login = input("Twój login: ")
    password = getpass("Twoje hasło: ")
    user = user_manager.authenticate_user(login, password)
    if not user:
        print("Nieprawidłowy login lub hasło. Nie można edytować.")
        return
    print(f"\nEdycja danych dla: {user.name} {user.surname}\n")
    print("  Dostępne pola:")
    for key, (field, label) in EDITABLE_FIELDS.items():
        current = getattr(user, field, "")
        if field == "password":
            current = "********"
        print(f"    {key} │ {label}: {current}")
    choice = input("\nWybierz numer pola: ").strip()
    if choice not in EDITABLE_FIELDS:
        print("Nieprawidłowy wybór.")
        return
    field, label = EDITABLE_FIELDS[choice]
    if field == "password":
        new_value = getpass(f"Nowe hasło: ")
    else:
        new_value = input(f"Nowa wartość dla '{label}': ")
    user_manager.edit_user(login, field, new_value)
