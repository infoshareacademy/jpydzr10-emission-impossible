import sys


def menu_0():
    while True:
        print("┌────── EMISSION IMPOSSIBLE ──────┐\n"
              "| 1 - Wczytaj projekt             |\n"
              "| 2 - Nowy projekt                |\n"
              "| 0 - Zakończ                     |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            return menu_1()                             # Tymczasowo pominięta opcja wczytywania/zapisu projektu
        elif option == '2':
            return menu_1()                             # Tymczasowo pominięta opcja wczytywania/zapisu projektu
        elif option == '0':
            sys.exit()
        else:
            print('Wprowadzono zły parametr!')


def menu_1():
    while True:
        print(f"┌────────── PROJEKT XYZ ──────────┐\n"   # Nazwa projektu do zastąpienia przez f string (nazwa pliku)
              "| 1 - Podsumowanie                |\n"
              "| 2 - Przedsiębiorstwo            |\n"
              "| 3 - Wskaźniki                   |\n"
              "| 4 - Przeliczniki                |\n"
              "| 5 - Dane emisyjne               |\n"
              "| 6 - Raporty                     |\n"
              "| 7 - Ustawienia                  |\n"
              "| 8 - ----------                  |\n"
              "| 9 - Zapisz                      |\n"
              "| 0 - Zakończ                     |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            return menu_1_1()
        elif option == '2':
            pass
        elif option == '3':
            pass
        elif option == '4':
            pass
        elif option == '5':
            pass
        elif option == '6':
            pass
        elif option == '7':
            pass
        elif option == '8':
            pass
        elif option == '9':
            pass
        elif option == '0':
            return menu_0()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_1():
    while True:
        print(f"┌──────────── PODSUMOWANIE ─────────────┐\n"        # Do uzupełnienia
              "| NAZWA FIRMY: EMISSION IMPOSSIBLE      |\n"
              "| NIP: 645065656                        |\n"
              "| Adres: ul. Kwiatowa, 00-000 Warszawa  |\n"
              "|                                       |\n"
              "|                                       |\n"
              "|                                       |\n"
              "|                                       |\n"
              "|                                       |\n"
              "|                                       |\n"
              "| 0 - Powrót                            |\n"
              "└───────────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '0':
            return menu_1()

menu_0()