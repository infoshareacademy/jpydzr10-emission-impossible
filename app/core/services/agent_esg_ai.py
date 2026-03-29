from google import genai
from app.application.use_cases import EmissionUseCases

class EmissionAgent:
    def __init__(self, api_key: str, data_folder: str = "data_files"):
        self.client = genai.Client(api_key=api_key)
        self.use_cases = EmissionUseCases(data_folder)
        self.model_id = "gemini-2.5-flash"

    def _prepare_context(self, company: str, year: int) -> str:
        summary = self.use_cases.generate_summary(year, year, company)
        errors_report = self.use_cases.repos.validate_all()

        if errors_report:
            error_details = ""
            for repo_name, errors in errors_report.items():
                error_details += f"\n- W module {repo_name}: {', '.join(errors)}"
        else:
            error_details = "Pliki źródłowe są poprawne."

        context = f"""
        DANE SYSTEMOWE DLA FIRMY: {company} (ROK {year})
        ---
        WYNIKI OBLICZEŃ (tCO2e):
        - Spalanie stacjonarne (Scope 1): {summary['scope1_stationary']}
        - Spalanie mobilne (Scope 1): {summary['scope1_mobile']}
        - Emisje niezorganizowane (Scope 1): {summary['scope1_fugitive']}
        - Emisje procesowe (Scope 1): {summary['scope1_process']}
        - ŁĄCZNIE: {summary['total']}

        STATUS DANYCH:
        {error_details}

        UWAGA: Jeśli wyniki wynoszą 0.000 mimo posiadania wpisów, oznacza to brak wskaźnika 
        w 'tbl_factors.csv' dla danego paliwa/procesu.
        """
        return context

    def chat(self, company: str, year: int, user_query: str):
        context = self._prepare_context(company, year)

        system_instruction = (
            "Jesteś ekspertem ds. raportowania ESG (Emission Impossible Assistant). "
            "Twoim zadaniem jest analiza danych o emisjach. Odpowiadaj konkretnie, "
            "używając terminologii technicznej, ale w sposób zrozumiały dla biznesu."
        )

        prompt = f"{context}\n\nUżytkownik pyta: {user_query}"

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                config={'system_instruction': system_instruction},
                contents=prompt
            )

            print("\n" + "ANALIZA AGENTA AI ".center(60, "═"))
            print(response.text)
            print("═" * 60 + "\n")

        except Exception as e:
            print(f"Błąd Agenta: {e}")