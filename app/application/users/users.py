# Obsługa użytkowników aplikacji

import getpass


from user_manager import UserManager
from getpass import getpass

user_manager = UserManager()


def user_prompt():
    login = input("Login: ")
    password = getpass("Password: ")
    user = user_manager.authenticate_user(login, password)
    if user:
        print(f"Welcome {user.name} {user.surname}!")
        return user
    else:
        print("Invalid login or password.")
        return None


def create_user():
    print("Create a new user:")
    name = input("Name: ")
    surname = input("Surname: ")
    email = input("Email: ")
    phone_number = input("Phone number: ")
    login = input("Login: ")
    password = getpass("Password: ")
    user_manager.add_user(name, surname, email, phone_number, login, password)


def edit_user():
    login = input("Your login: ")
    password = getpass("Your password: ")
    user = user_manager.authenticate_user(login, password)
    if not user:
        print("Invalid login. Cannot edit.")
        return
    print(f"Editing info for {user.name} {user.surname}")
    field = input("Field to edit (name, surname, email, phone_number, login, password): ")
    if field == "password":
        new_value = getpass("New password: ")
    else:
        new_value = input(f"New value for {field}: ")
    user_manager.edit_user(login, field, new_value)