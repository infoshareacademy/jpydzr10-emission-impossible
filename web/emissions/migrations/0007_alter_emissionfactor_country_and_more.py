import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0002_alter_companies_nip"),
        ("calculator", "0002_alter_fuelspec_supplier"),
        ("emissions", "0006_remove_fugitiveemission_notes"),
    ]

    operations = [
        # KROK 1: Dodaj tymczasową kolumnę country_id jako nullable
        migrations.AddField(
            model_name="emissionfactor",
            name="country_new",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="emission_factors",
                to="companies.countries",
                verbose_name="Kraj",
            ),
        ),
        # KROK 2: Wypełnij country_new na podstawie starego pola country (string)
        migrations.RunSQL(
            sql="""
                UPDATE tbl_factors f
                SET country_new_id = c.id
                FROM companies_countries c
                WHERE f.country = c.code_alfa_2
            """,
            reverse_sql="""
                UPDATE tbl_factors f
                SET country = c.code_alfa_2
                FROM companies_countries c
                WHERE f.country_new_id = c.id
            """,
        ),
        # KROK 3: Usuń starą kolumnę country (CharField)
        migrations.RemoveField(
            model_name="emissionfactor",
            name="country",
        ),
        # KROK 4: Zmień nazwę country_new na country
        migrations.RenameField(
            model_name="emissionfactor",
            old_name="country_new",
            new_name="country",
        ),
        # KROK 5: Zmień fuel w StationaryCombustion z CharField na ForeignKey
        migrations.AddField(
            model_name="stationarycombustion",
            name="fuel_new",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="stationary_combustions",
                to="calculator.fueltype",
                verbose_name="Paliwo",
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE tbl_stationary_combustion sc
                SET fuel_new_id = ft.id
                FROM calculator_fueltype ft
                WHERE sc.fuel = ft.name
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name="stationarycombustion",
            name="fuel",
        ),
        migrations.RenameField(
            model_name="stationarycombustion",
            old_name="fuel_new",
            new_name="fuel",
        ),
        # KROK 6: Zmień fuel w MobileCombustion z CharField na ForeignKey
        migrations.AddField(
            model_name="mobilecombustion",
            name="fuel_new",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="mobile_combustions",
                to="calculator.fueltype",
                verbose_name="Paliwo",
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE tbl_mobile_combustion mc
                SET fuel_new_id = ft.id
                FROM calculator_fueltype ft
                WHERE mc.fuel = ft.name
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name="mobilecombustion",
            name="fuel",
        ),
        migrations.RenameField(
            model_name="mobilecombustion",
            old_name="fuel_new",
            new_name="fuel",
        ),
    ]
