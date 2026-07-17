from django.utils.translation import gettext_lazy as _

APPS_REGISTRY = [
    {"url_name": "reports:ghg-report", "title": _("Raporty"), "icon": "book_2"},
    {
        "url_name": "companies:companies-list",
        "title": _("Przedsiębiorstwo"),
        "icon": "business",
    },
    {
        "url_name": "emissions:factor-list",
        "title": _("Wskaźniki Emisji"),
        "icon": "pie_chart",
    },
    {"url_name": "calculator:dashboard", "title": _("Przeliczniki"), "icon": "bar_chart"},
    {
        "url_name": "what_if:reduction-target-list",
        "title": _("Cele i symulacje"),
        "icon": "local_fire_department",
    },
    {
        "url_name": "accounts:company-users-list",
        "title": _("Użytkownicy"),
        "icon": "group",
    },
    {
        "url_name": "ai_services:global_assistant",
        "title": _("AI Asystent ESG"),
        "icon": "auto_awesome",
    },
    {
        "url_name": "communications:thread_list",
        "title": _("Komunikacja e-mail"),
        "icon": "mail",
    },
    {
        "url_name": "workflow:admin_list",
        "title": _("Audyt i Weryfikacja"),
        "icon": "fact_check",
        "admin_only": True,
    },
]