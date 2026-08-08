import logging

from codecarbon import EmissionsTracker

from .models import UserCarbonFootprint

logger = logging.getLogger(__name__)


class PerUserCarbonTrackingMiddleware:

  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if not request.user.is_authenticated or request.path.startswith(
        ('/static/', '/media/', '/admin/')
    ):
      return self.get_response(request)

    tracker = EmissionsTracker(
        project_name=f'User_{request.user.username}',
        output_dir='./emissions_logs',
        log_level='ERROR',
        save_to_file=False,
    )

    tracker.start()
    response = self.get_response(request)
    emissions = tracker.stop()

    if emissions and emissions > 0:
      stats, created = UserCarbonFootprint.objects.get_or_create(
          user=request.user
      )
      stats.total_emissions_kg += emissions
      stats.total_requests += 1
      stats.save()

    return response