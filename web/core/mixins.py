from django.db.models import F

from .models import UserPageView


class PageViewTrackerMixin:
    """
    Mixin zliczający wizyty na danym widoku, aktualizujący stan bezpośrednio
    w silniku bazy danych z pominięciem pamięci Pythona (F expressions).
    """

    tracked_view_name = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self._track_page_view(request)
        return super().get(request, *args, **kwargs)

    def _track_page_view(self, request):
        name = self.tracked_view_name or request.resolver_match.view_name
        obj, created = UserPageView.objects.get_or_create(
            user=request.user,
            view_name=name,
            defaults={"url_path": request.path, "visit_count": 1},
        )

        if not created:
            UserPageView.objects.filter(pk=obj.pk).update(
                visit_count=F("visit_count") + 1, url_path=request.path
            )

