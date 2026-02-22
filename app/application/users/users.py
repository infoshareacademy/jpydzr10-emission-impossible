# Obsługa użytkowników aplikacji

import getpass

# def user_prompt():
#     username = input('Podaj nazwę użytkownika:')
#     password = input('Podaj hasło:')                            # Prompt o hasło na potrzeby testów w IDE
# #    password = getpass.getpass('Podaj hasło:')                 # Prompt o hasło 'produkcyjny' - działa w terminalu, w IDE powoduje błąd
#     return authenticate_user(username, password)
#
# def authenticate_user(username, password):                      # Do uzupełnienia
#     return True



class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password