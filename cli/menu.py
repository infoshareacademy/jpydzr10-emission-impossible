import sys
from app.defaults import *


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
        print(f"┌──────── {project_name:^15.15} ────────┐\n"
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
            return menu_1_2()
        elif option == '3':
            return menu_1_3()
        elif option == '4':
            return menu_1_4()
        elif option == '5':
            return menu_1_5()
        elif option == '6':
            return menu_1_6()
        elif option == '7':
            return menu_1_7()
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
        print(f"┌──────────────────────── PODSUMOWANIE ─────────────────────────┐\n"        # Do uzupełnienia
              f"| NAZWA FIRMY:{company:<50.50}|\n"
              f"| ADRES:      {company_address:<50.50}|\n"
              f"| TELEFON:    {company_tel:<15.15}  E-MAIL: {company_mail:<25.25}|\n"
              f"|---------------------------------------------------------------|\n"
              f"| Okres sprawozdawczy: 2026 r.                                  |\n"        # Dane przykładowe
              f"| Ślad węglowy (CO2e): 123 566 789                              |\n"
              f"|                        DO UZUPEŁNIENIA                        |\n"
              f"|                                                               |\n"
              f"|                                                               |\n"
              f"|                                                               |\n"
              f"|                                                               |\n"
              f"| 0 - Powrót                                                    |\n"
              f"└───────────────────────────────────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '0':
            return menu_1()


def menu_1_2():
    while True:
        print("┌──────── PRZEDSIĘBIORSTWO ───────┐\n"
              "| 1 - Wyświetl                    |\n"
              "| 2 - Edytuj                      |\n"
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_3():
    while True:
        print("┌─────────── WSKAŹNIKI ───────────┐\n"
              "| 1 - Wyświetl                    |\n"
              "| 2 - Wczytaj z pliku (zastąp)    |\n"
              "| 3 - Wczytaj z pliku (dodaj)     |\n"
              "| 4 - Dodaj                       |\n"
              "| 5 - Edytuj                      |\n"
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '3':
            pass
        elif option == '4':
            pass
        elif option == '5':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_4():
    while True:
        print("┌───────── PRZELICZNIKI ──────────┐\n"
              "| 1 - Wyświetl                    |\n"
              "| 2 - Wczytaj z pliku (zastąp)    |\n"
              "| 3 - Wczytaj z pliku (dodaj)     |\n"
              "| 4 - Dodaj                       |\n"
              "| 5 - Edytuj                      |\n"
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '3':
            pass
        elif option == '4':
            pass
        elif option == '5':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_5():
    while True:
        print("┌───────── DANE EMISYJNE ─────────┐\n"
              "| 1 - Spalanie stacjonarne        |\n"
              "| 2 - Spalanie mobilne            |\n"
              "| 3 - Emisje procesowe            |\n"
              "| 4 - Emisje niezorganizowane     |\n"
              "| 5 - Energia                     |\n"
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '3':
            pass
        elif option == '4':
            pass
        elif option == '5':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_6():
    while True:
        print("┌──────────── RAPORTY ────────────┐\n"
              "| 1 - Generuj Raport 1            |\n"
              "| 2 - Generuj Raport 2            |\n"
              "| 3 - Generuj Raport 3            |\n"              
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '3':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')


def menu_1_7():
    while True:
        print("┌─────────── USTAWIENIA ──────────┐\n"
              "| 1 - Język                       |\n"
              "| 2 - Jednostki                   |\n"
              "|                                 |\n"
              "| 0 - Powrót                      |\n"
              "└─────────────────────────────────┘")
        option = input('Wybierz opcję: ')
        if option == '1':
            pass
        elif option == '2':
            pass
        elif option == '0':
            return menu_1()
        else:
            print('Wprowadzono zły parametr!')