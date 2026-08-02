from typing import TypedDict

from companies.models import Companies
from django.db.models import F, FloatField, Sum
from django.db.models.functions import Coalesce

from .models import MobileCombustion, StationaryCombustion


class Scope1Summary(TypedDict):
    mobile_total: float
    stationary_total: float
    grand_total: float

class EmissionCalculatorService:
    """
    Serwis odpowiedzialny za agregacje emisyjne.
    Operacje wykonywane są bezwzględnie po stronie bazy danych (PostgreSQL).
    """

    @staticmethod
    def calculate_scope_1(company: Companies, year: int) -> Scope1Summary:
        # Zabezpieczenie przed błędem z poprzednich rozmów - używamy poprawnego workflow_status
        base_filters = {
            "company": company,
            "year": year,
            "workflow_status": "APPROVED"
        }

        mobile_agg = MobileCombustion.objects.filter(**base_filters).aggregate(
            total=Coalesce(
                Sum(F('fuel_consumed') * F('emission_factor_value'), output_field=FloatField()),
                0.0
            )
        )

        stationary_agg = StationaryCombustion.objects.filter(**base_filters).aggregate(
            total=Coalesce(
                Sum(F('fuel_consumed') * F('emission_factor_value'), output_field=FloatField()),
                0.0
            )
        )

        mobile_total = mobile_agg['total']
        stationary_total = stationary_agg['total']

        return {
            "mobile_total": mobile_total,
            "stationary_total": stationary_total,
            "grand_total": mobile_total + stationary_total
        }