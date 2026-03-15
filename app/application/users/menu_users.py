
from users import user_prompt, create_user, edit_user

def menu_users():
    """
    Menu for handling user operations:
    1 - Login
    2 - Create new user
    3 - Edit my data
    0 - Back to main menu
    """
    while True:
        print(
            "┌────────── USERS ──────────┐\n"
            "| 1 - Login                 |\n"
            "| 2 - Create new user       |\n"
            "| 3 - Edit my data          |\n"
            "| 0 - Back                  |\n"
            "└───────────────────────────┘"
        )
        option = input("Choose an option: ")
        if option == "1":
            user_prompt()
        elif option == "2":
            create_user()
        elif option == "3":
            edit_user()
        elif option == "0":
            return  # back to main menu
        else:
            print("Invalid option!")