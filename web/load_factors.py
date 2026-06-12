import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from emissions.models import EmissionFactor
from companies.models import Countries

with open('../data_files/tbl_factors.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        print(f"Row: {row}")
        country = Countries.objects.filter(name=row['country']).first()
        if not country:
            print(f"Country not found: {row['country']}")
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
