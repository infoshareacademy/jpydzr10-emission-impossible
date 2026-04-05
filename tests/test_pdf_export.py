"""Testy eksportu PDF — sprawdza generowanie plików PDF z raportów emisyjnych."""

import os
import pytest
from decimal import Decimal


class TestPdfExportSummary:
    """Testy eksportu podsumowania emisji do PDF."""

    def test_export_creates_pdf_file(self, uc, tmp_path):
        """Eksport podsumowania tworzy plik PDF."""
        from app.application.pdf_export import export_summary_pdf, EXPORT_FOLDER

        summary = uc.generate_summary(2025, 2025, "TestFirma A")
        # Nadpisz folder eksportu na tmp
        import app.application.pdf_export as pdf_mod
        original_folder = pdf_mod.EXPORT_FOLDER
        pdf_mod.EXPORT_FOLDER = str(tmp_path)

        try:
            path = export_summary_pdf(summary, "TestFirma A")
            assert os.path.isfile(path)
            assert path.endswith(".pdf")
            # Plik powinien mieć rozsądny rozmiar (> 1KB)
            assert os.path.getsize(path) > 1000
        finally:
            pdf_mod.EXPORT_FOLDER = original_folder

    def test_export_with_custom_filename(self, uc, tmp_path):
        """Eksport z własną nazwą pliku."""
        from app.application.pdf_export import export_summary_pdf
        import app.application.pdf_export as pdf_mod
        original_folder = pdf_mod.EXPORT_FOLDER
        pdf_mod.EXPORT_FOLDER = str(tmp_path)

        try:
            summary = uc.generate_summary(2025, 2025, "TestFirma A")
            path = export_summary_pdf(summary, "TestFirma A", filename="test_raport.pdf")
            assert os.path.basename(path) == "test_raport.pdf"
            assert os.path.isfile(path)
        finally:
            pdf_mod.EXPORT_FOLDER = original_folder

    def test_export_with_zero_emissions(self, uc, tmp_path):
        """Eksport działa nawet gdy wszystkie emisje = 0."""
        from app.application.pdf_export import export_summary_pdf
        import app.application.pdf_export as pdf_mod
        original_folder = pdf_mod.EXPORT_FOLDER
        pdf_mod.EXPORT_FOLDER = str(tmp_path)

        try:
            # Firma bez danych
            summary = uc.generate_summary(2020, 2020, "NieistniejącaFirma")
            path = export_summary_pdf(summary, "NieistniejącaFirma")
            assert os.path.isfile(path)
        finally:
            pdf_mod.EXPORT_FOLDER = original_folder


class TestPdfExportTrend:
    """Testy eksportu trendów do PDF."""

    def test_export_trend_creates_pdf(self, uc, tmp_path):
        """Eksport trendów tworzy plik PDF."""
        from app.application.pdf_export import export_trend_pdf
        import app.application.pdf_export as pdf_mod
        original_folder = pdf_mod.EXPORT_FOLDER
        pdf_mod.EXPORT_FOLDER = str(tmp_path)

        try:
            trends = uc.generate_trend_report("TestFirma A", 2024, 2025)
            path = export_trend_pdf(trends, "TestFirma A", 2024, 2025)
            assert os.path.isfile(path)
            assert path.endswith(".pdf")
            assert os.path.getsize(path) > 1000
        finally:
            pdf_mod.EXPORT_FOLDER = original_folder
