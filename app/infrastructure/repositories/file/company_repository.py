import csv
import os

# Ścieżka do folderu z plikami CSV
FOLDER_PATH = "data_files"


def read_csv(filename: str) -> list:
    """Wczytuje dane z pojedynczego pliku CSV i zwraca listę słowników."""

    file_path = os.path.join(FOLDER_PATH, filename)

    # Otwieramy plik - utf-8 obsługuje polskie znaki,
    # newline='' zapobiega podwójnym pustym liniom
    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        # Zamieniamy na listę od razu, bo po zamknięciu pliku
        # nie możemy już czytać z readera
        rows = list(reader)

    return rows


def read_all_csv() -> dict:
    """Wczytuje wszystkie pliki CSV z folderu i zwraca słownik
    w formacie {nazwa_pliku: lista_wierszy}."""

    all_data = {}

    # Przechodzimy przez wszystkie pliki w folderze
    for filename in os.listdir(FOLDER_PATH):

        # Pomijamy pliki które nie są CSV (np. .gitkeep)
        if not filename.endswith('.csv'):
            continue

        # Wczytujemy każdy plik i zapisujemy pod jego nazwą
        all_data[filename] = read_csv(filename)

    return all_data


def display_csv(rows: list, title: str = "") -> None:
    """Wyświetla dane z jednego pliku CSV w czytelnych kolumnach."""

    if not rows:
        print("Brak danych w pliku.")
        return

    col_width = 20

    # Wyświetlamy tytuł sekcji jeśli został podany
    if title:
        print(f"\n{'=' * 60}")
        print(f" Plik: {title}")
        print(f"{'=' * 60}")

    # Pobieramy nazwy kolumn z pierwszego wiersza
    headers = rows[0].keys()

    # Drukujemy nagłówki - ljust dopełnia każdą nazwę spacjami
    # do szerokości col_width żeby kolumny były równe
    header_line = "".join(h.ljust(col_width) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    # Drukujemy każdy wiersz danych w tych samych kolumnach
    for row in rows:
        print("".join(str(row[h]).ljust(col_width) for h in headers))


def display_all_csv(all_data: dict) -> None:
    """Wyświetla dane ze wszystkich wczytanych plików CSV."""

    if not all_data:
        print("Brak plików CSV w folderze.")
        return

    # Dla każdego pliku wywołujemy display_csv z nazwą pliku jako tytułem
    for filename, rows in all_data.items():
        display_csv(rows, title=filename)


def add_row(filename: str, new_data: dict) -> None:
    """Dodaje nowy wiersz na końcu wskazanego pliku CSV."""

    file_path = os.path.join(FOLDER_PATH, filename)

    # Tryb 'a' (append) dopisuje na końcu pliku
    # bez nadpisywania istniejących danych
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        # DictWriter zapisuje słowniki jako wiersze CSV
        # fieldnames pobiera nazwy kolumn z kluczy słownika
        writer = csv.DictWriter(file, fieldnames=new_data.keys())

        # Dopisujemy nowy wiersz
        # np. {"id": "3", "company": "Firma Y", "fuel": "węgiel", ...}
        writer.writerow(new_data)

    print(f"Dodano nowy wiersz do pliku: {filename}")


def edit_row_by_id(filename: str, row_id: str, column: str, new_value: str) -> None:
    """Znajduje wiersz po ID i zmienia wartość w podanej kolumnie."""

    # Wczytujemy wszystkie dane do pamięci
    # bo musimy zmodyfikować jeden wiersz i zapisać wszystko od nowa
    rows = read_csv(filename)

    # Sprawdzamy czy plik w ogóle ma kolumnę 'id'
    if rows and "id" not in rows[0]:
        print("Ten plik nie posiada kolumny 'id'.")
        return

    # Flaga informująca czy znaleźliśmy wiersz z podanym id
    found = False

    for row in rows:
        if row["id"] == row_id:

            # Sprawdzamy czy podana kolumna istnieje w pliku
            if column not in row:
                print(f"Kolumna '{column}' nie istnieje w pliku.")
                return

            # Zmieniamy wartość w podanej kolumnie
            row[column] = new_value
            found = True
            break  # id jest unikalne - nie ma sensu szukać dalej

    if not found:
        print(f"Nie znaleziono wiersza z id: {row_id}")
        return

    file_path = os.path.join(FOLDER_PATH, filename)

    # Tryb 'w' (write) nadpisuje cały plik
    # dlatego wcześniej wczytaliśmy wszystkie dane do pamięci
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())

        # Najpierw zapisujemy nagłówki (nazwy kolumn)
        writer.writeheader()

        # Potem wszystkie wiersze - już ze zmienioną wartością
        writer.writerows(rows)

    print(f"Zmieniono '{column}' na '{new_value}' dla id: {row_id} w pliku: {filename}")