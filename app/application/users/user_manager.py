import csv
import os
import re
from getpass import getpass
from dataclasses import dataclass
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data_files", ".env")
load_dotenv(env_path)

FOLDER_PATH = "data_files"
USERS_FILE = "tbl_users.csv"
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
        # Basic validations
        if not all([name, surname, email, phone_number, login, password]):
            print("All fields are required.")
            return None
        if not re.match(EMAIL_REGEX, email):
            print("Invalid email format.")
            return None
        if any(u.login == login for u in self.users):
            print(f"Login '{login}' already exists.")
            return None

        new_user = User(name, surname, email, phone_number, login, password)
        self.users.append(new_user)
        self._save_users()
        print(f"✅ User '{login}' added successfully.")
        return new_user

    def authenticate_user(self, login, password):
        for user in self.users:
            if user.login == login and user.password == password:
                return user
        return None

    def edit_user(self, login, field, new_value):
        for user in self.users:
            if user.login == login:
                if not new_value:
                    print("Value cannot be empty.")
                    return False
                if field == "email" and not re.match(EMAIL_REGEX, new_value):
                    print("Invalid email format.")
                    return False
                if hasattr(user, field):
                    setattr(user, field, new_value)
                    self._save_users()
                    print(f"Updated {field} for {login}.")
                    return True
                else:
                    print(f"Field '{field}' does not exist.")
                    return False
        print(f"User '{login}' not found.")
        return False

    def list_users(self):
        print("\nCurrent users:")
        for u in self.users:
            print(f"{u.login} - {u.name} {u.surname}")
        print()