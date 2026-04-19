"""
Eksport raportu emisji do PDF.

Generuje profesjonalny dokument PDF z podsumowaniem emisji
na podstawie danych z generate_summary() i generate_trend_report().
"""

import os
import unicodedata
from datetime import datetime
from decimal import Decimal
from fpdf import FPDF

EXPORT_FOLDER = os.path.join("data_files", "export")


_CHAR_MAP = {
    "\u2013": "-",   # en-dash →  -
    "\u2014": "-",   # em-dash → -
    "\u2018": "'",   # lewy cudzysłów
    "\u2019": "'",   # prawy cudzysłów
    "\u201c": '"',   # lewy podwójny cudzysłów
    "\u201d": '"',   # prawy podwójny cudzysłów
    "\u2026": "...", # wielokropek
    "\u2190": "<-",  # strzałka w lewo
    "\u2192": "->",  # strzałka w prawo
    "\u2191": "^",   # strzałka w górę
    "\u2193": "v",   # strzałka w dół
    "\u2022": "*",   # bullet
    "\u00b2": "2",   # ² (CO₂)
    "\u2082": "2",   # ₂ (CO₂)
    "\u00d7": "x",   # ×
}


def _safe_text(text: str) -> str:
    """Konwertuje tekst do zakresu Latin-1 (Helvetica nie obsługuje pełnego Unicode)."""
    for orig, repl in _CHAR_MAP.items():
        text = text.replace(orig, repl)
    nfkd = unicodedata.normalize("NFKD", text)
    result = "".join(c for c in nfkd if not unicodedata.combining(c))
    result = result.replace("\u0142", "l").replace("\u0141", "L")
    return result.encode("latin-1", errors="replace").decode("latin-1")


class EmissionPdfReport(FPDF):
    """Raport PDF z podsumowaniem emisji GHG."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()

    def cell(self, w=None, h=None, text="", *args, **kwargs):
        """Nadpisanie — automatycznie konwertuje polskie znaki na ASCII."""
        return super().cell(w, h, _safe_text(str(text)), *args, **kwargs)

    def multi_cell(self, w, h=None, text="", *args, **kwargs):
        """Nadpisanie — automatycznie konwertuje polskie znaki na ASCII."""
        return super().multi_cell(w, h, _safe_text(str(text)), *args, **kwargs)

    def _section_title(self, title: str):
        """Nagłówek sekcji."""
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def _key_value_row(self, key: str, value: str, bold_value: bool = False):
        """Wiersz klucz-wartość."""
        self.set_font("Helvetica", "", 10)
        self.cell(80, 7, key, new_x="RIGHT")
        self.set_font("Helvetica", "B" if bold_value else "", 10)
        self.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

    def _table_header(self, columns: list[tuple[str, int]]):
        """Nagłówek tabeli."""
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(220, 220, 220)
        for name, width in columns:
            self.cell(width, 7, name, border=1, fill=True, align="C")
        self.ln()

    def _table_row(self, columns: list[tuple[str, int]], align: str = "C"):
        """Wiersz tabeli."""
        self.set_font("Helvetica", "", 9)
        for value, width in columns:
            self.cell(width, 7, value, border=1, align=align)
        self.ln()

    def header(self):
        """Nagłówek strony."""
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(41, 128, 185)
        self.cell(0, 12, "EMISSION IMPOSSIBLE", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Raport emisji gazow cieplarnianych (GHG)", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)
        self.set_draw_color(41, 128, 185)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        """Stopka strony."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 10, f"Wygenerowano: {date_str}  |  Strona {self.page_no()}/{{nb}}", align="C")


def _fmt(value: Decimal) -> str:
    """Formatuje Decimal do stringa z 3 miejscami."""
    return f"{value:.3f}"


def export_summary_pdf(summary: dict, company: str, filename: str = None) -> str:
    """Eksportuje podsumowanie emisji do pliku PDF.

    Args:
        summary: wynik generate_summary()
        company: nazwa firmy
        filename: opcjonalna nazwa pliku (bez sciezki)

    Returns:
        sciezka do wygenerowanego pliku
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    if filename is None:
        safe_name = company.replace(" ", "_").replace(".", "")
        years = summary.get("years_label", "")
        filename = f"raport_{safe_name}_{years}.pdf"

    filepath = os.path.join(EXPORT_FOLDER, filename)

    pdf = EmissionPdfReport()
    pdf.alias_nb_pages()
    pdf._section_title("Informacje ogolne")
    pdf._key_value_row("Firma:", company)
    pdf._key_value_row("Okres:", summary.get("years_label", ""))
    pdf._key_value_row("Data raportu:", datetime.now().strftime("%Y-%m-%d"))
    pdf.ln(4)
    pdf._section_title("Scope 1 - Emisje bezposrednie")

    cols = [("Kategoria", 90), ("Emisja [tCO2e]", 50)]
    pdf._table_header(cols)

    scope1_items = [
        ("Spalanie stacjonarne", summary["scope1_stationary"]),
        ("Spalanie mobilne", summary["scope1_mobile"]),
        ("Emisje niezorganizowane", summary["scope1_fugitive"]),
        ("Emisje procesowe", summary["scope1_process"]),
    ]
    scope1_total = sum(v for _, v in scope1_items)

    for name, value in scope1_items:
        pdf._table_row([(name, 90), (_fmt(value), 50)])

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(90, 7, "RAZEM Scope 1", border=1, fill=True, align="C")
    pdf.cell(50, 7, _fmt(scope1_total), border=1, align="C")
    pdf.ln(6)

    pdf._section_title("Scope 2 - Emisje posrednie (energia)")

    cols = [("Kategoria", 90), ("Emisja [tCO2e]", 50)]
    pdf._table_header(cols)
    pdf._table_row([("Zuzycie energii", 90), (_fmt(summary["scope2_energy"]), 50)])

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(90, 7, "RAZEM Scope 2", border=1, fill=True, align="C")
    pdf.cell(50, 7, _fmt(summary["scope2_energy"]), border=1, align="C")
    pdf.ln(6)

    pdf._section_title("Podsumowanie")

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 12, f"LACZNA EMISJA (Scope 1 + 2): {_fmt(summary['total'])} tCO2e",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    if summary["total"] > 0:
        pdf.set_font("Helvetica", "", 10)
        s1_pct = (scope1_total / summary["total"] * 100).quantize(Decimal("0.1"))
        s2_pct = (summary["scope2_energy"] / summary["total"] * 100).quantize(Decimal("0.1"))
        pdf._key_value_row("Udzial Scope 1:", f"{s1_pct}%")
        pdf._key_value_row("Udzial Scope 2:", f"{s2_pct}%")

    pdf.ln(6)
    pdf._section_title("Metodologia")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5,
        "Obliczenia zgodne z GHG Protocol Corporate Standard (Revised Edition). "
        "Wskazniki emisji: KOBiZE 2024, DEFRA 2024, IPCC AR5. "
        "Emisja deklarowana (z raportu) ma priorytet nad wyliczona ze wskaznikow.")

    pdf.output(filepath)
    return filepath


def export_trend_pdf(trends: list[dict], company: str, year_from: int, year_to: int,
                     filename: str = None) -> str:
    """Eksportuje raport trendów do pliku PDF.

    Args:
        trends: wynik generate_trend_report()
        company: nazwa firmy
        year_from, year_to: zakres lat
        filename: opcjonalna nazwa pliku

    Returns:
        sciezka do wygenerowanego pliku
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    if filename is None:
        safe_name = company.replace(" ", "_").replace(".", "")
        filename = f"trendy_{safe_name}_{year_from}-{year_to}.pdf"

    filepath = os.path.join(EXPORT_FOLDER, filename)

    pdf = EmissionPdfReport()
    pdf.alias_nb_pages()
    pdf._section_title("Raport trendow emisji")
    pdf._key_value_row("Firma:", company)
    pdf._key_value_row("Zakres lat:", f"{year_from} - {year_to}")
    pdf._key_value_row("Data raportu:", datetime.now().strftime("%Y-%m-%d"))
    pdf.ln(4)
    pdf._section_title("Emisje rok do roku")

    col_w = [20, 30, 30, 30, 30, 30]
    headers = [("Rok", col_w[0]), ("Scope 1", col_w[1]), ("Scope 2", col_w[2]),
               ("Lacznie", col_w[3]), ("Zmiana %", col_w[4])]
    pdf._table_header(headers)

    for t in trends:
        scope1 = t.get("scope1_total", Decimal("0"))
        scope2 = t.get("scope2_energy", Decimal("0"))
        total = t.get("total", Decimal("0"))
        change = t.get("change_pct")
        change_str = f"{change:+.1f}%" if change is not None else "-"

        pdf._table_row([
            (str(t["year"]), col_w[0]),
            (_fmt(scope1), col_w[1]),
            (_fmt(scope2), col_w[2]),
            (_fmt(total), col_w[3]),
            (change_str, col_w[4]),
        ])

    if len(trends) >= 2:
        first = trends[0]["total"]
        last = trends[-1]["total"]
        if first > 0:
            overall = ((last - first) / first * 100).quantize(Decimal("0.1"))
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 11)
            direction = "wzrost" if overall > 0 else "spadek"
            pdf.cell(0, 10,
                     f"Zmiana {year_from} -> {year_to}: {direction} o {abs(overall)}% "
                     f"({_fmt(first)} -> {_fmt(last)} tCO2e)",
                     new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.output(filepath)
    return filepath
