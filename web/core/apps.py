import threading

from codecarbon import EmissionsTracker
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

def ready(self):
    import os

    if os.environ.get('RUN_MAIN') == 'true':

      def start_global_tracker():
        global_tracker = EmissionsTracker(
            project_name='Emission Impossible Global Uptime',
            output_dir='./global_emissions',
            measure_power_secs=60,  # Pomiar co minutę
        )
        global_tracker.start()

      t = threading.Thread(target=start_global_tracker, daemon=True)
      t.start()