from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache

from core.models import UserCarbonFootprint

User = get_user_model()

@shared_task
def flush_carbon_footprints_to_db():
    """Zadanie Celery okresowo przenoszące dane z Redisa do PostgreSQL"""
    if not hasattr(cache, 'client'):
        return

    redis_client = cache.client.get_client()

    active_user_ids = redis_client.smembers('active_carbon_users')
    if not active_user_ids:
        return

    for user_id_bytes in active_user_ids:
        user_id = int(user_id_bytes.decode('utf-8'))
        req_cache_key = f'carbon_reqs_user_{user_id}'

        reqs_count_str = redis_client.get(req_cache_key)
        if not reqs_count_str:
            continue

        reqs_count = int(reqs_count_str)
        redis_client.delete(req_cache_key)

        estimated_emissions = reqs_count * 0.00005

        try:
            stats, created = UserCarbonFootprint.objects.get_or_create(user_id=user_id)
            stats.total_emissions_kg += estimated_emissions
            stats.total_requests += reqs_count
            stats.save()
        except Exception as e:
            print(f"Błąd w flush_carbon: {e}")

        redis_client.delete('active_carbon_users')