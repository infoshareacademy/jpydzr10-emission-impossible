from codecarbon import EmissionsTracker
import app.interfaces.cli.menu as cli

tracker = EmissionsTracker(
    project_name="emission-impossible",
    output_dir="data_files",
    output_file="emissions.csv",
    tracking_mode="process",
    log_level="warning",
)

tracker.start()
try:
    cli.menu_0()
finally:
    emissions = tracker.stop()
    if emissions is not None:
        print(f"\n--- Ślad węglowy sesji: {emissions:.6f} kg CO2eq ---")
