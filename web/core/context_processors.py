from .registry import APPS_REGISTRY


def available_apps(request):
    if not request.user.is_authenticated:
        return {"available_apps": []}

    apps = []
    for app in APPS_REGISTRY:
        if app.get("admin_only") and not (
            request.user.is_staff or request.user.is_superuser
        ):
            continue
        apps.append(app)

    return {"available_apps": apps}
