import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from emissions.models import EmissionFactor
from companies.models import Countries

# ← ZAŁADUJ Z CSV:
with open('../data_files/tbl_factors.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        country = Countries.objects.filter(name=row['country']).first()
        if country:
            EmissionFactor.objects.update_or_create(
                factor_name=row['factor_name'],
                year=int(row['year']),
                country=country,
                defaults={
                    'factor': float(row['factor']),
                    'unit_factor': row['unit_factor'],
                    'source': row.get('source', ''),
                }
            )
            count += 1

print(f'Załadowano {count} wskaźników!')

# ← DODAJ CUSTOM WSKAŹNIKI:
poland = Countries.objects.get(name='Polska')

years = list(range(2010, 2025))  # 2010–2024

custom_factors = []

# Energia elektryczna z OZE
for y in years:
    custom_factors.append(
        ('Energia elektryczna z OZE', y, 0.815, 'tCO2e/MWh')
    )

# Energia elektryczna nie OZE
for y in years:
    custom_factors.append(
        ('Energia elektryczna nie OZE', y, 0.815, 'tCO2e/MWh')
    )

# Ciepło z OZE
for y in years:
    custom_factors.append(
        ('Ciepło z OZE', y, 0.32, 'tCO2e/GJ')
    )

# Ciepło nie OZE
for y in years:
    custom_factors.append(
        ('Ciepło nie OZE', y, 0.32, 'tCO2e/GJ')
    )

# Chłód z OZE
for y in years:
    custom_factors.append(
        ('Chłód z OZE', y, 0.32, 'tCO2e/GJ')
    )

# Chłód nie OZE
for y in years:
    custom_factors.append(
        ('Chłód nie OZE', y, 0.32, 'tCO2e/GJ')
    )

# Para Techniczna z OZE
for y in years:
    custom_factors.append(
        ('Para Techniczna z OZE', y, 0.32, 'tCO2e/GJ')
    )

# Para Techniczna nie OZE
for y in years:
    custom_factors.append(
        ('Para Techniczna nie OZE', y, 0.32, 'tCO2e/GJ')
    )

# Zapis do bazy
for factor_name, year, factor, unit_factor in custom_factors:
    EmissionFactor.objects.get_or_create(
        factor_name=factor_name,
        year=year,
        country=poland,
        defaults={
            'factor': factor,
            'unit_factor': unit_factor,
            'source': 'Custom'
        }
    )

print('Dodano custom wskaźniki!')