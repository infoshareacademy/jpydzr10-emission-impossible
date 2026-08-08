import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class FastCarbonTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Sprawdź globalną flagę – jeśli wyłączone, pomiń całkowicie
        if not getattr(settings, "ENABLE_CARBON_TRACKING", False):
            return self.get_response(request)

        response = self.get_response(request)

        # 2. Śledź tylko zalogowanych użytkowników (pomijając statyki i admina)
        if request.user.is_authenticated and not request.path.startswith(
            ("/static/", "/media/", "/admin/")
        ):
            try:
                user_id = request.user.id
                req_cache_key = f"carbon_reqs_user_{user_id}"

                # Inkrementuj licznik zapytań w Redisie (błyskawiczne w pamięci RAM)
                try:
                    cache.incr(req_cache_key)
                except ValueError:
                    cache.set(req_cache_key, 1, timeout=86400)  # Ważne 24h

                # Zapamiętaj ID aktywnego użytkownika w zbiorze Redis (żeby Celery wiedziało, kogo zaktualizować)
                # (Wymaga pakietu django-redis)
                if hasattr(cache, "client"):
                    redis_client = cache.client.get_client()
                    redis_client.sadd("active_carbon_users", user_id)

            except Exception as e:
                logger.error(f"Błąd zapisu śladu węglowego do Redisa: {e}")

        return response
