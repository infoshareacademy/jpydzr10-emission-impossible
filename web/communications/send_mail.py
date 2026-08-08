from accounts.models import CustomUser
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.translation import gettext as _  # <--- KLUCZOWY IMPORT DLA TŁUMACZEŃ


def send_thread_notification(request, thread, message, is_new=False):
    """
    Wysyła powiadomienie e-mail o nowym wątku lub nowej wiadomości.
    Odbiorcy: Uczestnicy wątku + osoby ze statusem can_save dla danej spółki.
    """
    save_users = CustomUser.objects.filter(
        company_permissions__company=thread.company, company_permissions__can_save=True
    )

    participant_ids = thread.messages.values_list("sender_id", flat=True).distinct()
    participants = CustomUser.objects.filter(id__in=participant_ids)

    emails = set()
    for u in save_users.union(participants):
        if u.email and u != message.sender:
            emails.add(u.email)

    if not emails:
        return

    thread_url = request.build_absolute_uri(
        reverse("communications:thread_detail", args=[thread.id])
    )

    akcja = _("Nowe zgłoszenie") if is_new else _("Nowa odpowiedź")
    subject = f"[Emission Impossible] {akcja}: {thread.subject} - {thread.company.name}"

    body = (
        f"{_('Szanowni Państwo')},\n\n"
        f"{_('Użytkownik')} {message.sender.username} {_('dodał nową wiadomość w wątku dotyczącym spółki')} {thread.company.name}.\n\n"
        f"{_('Kategoria')}: {thread.get_category_display()}\n"
        f"{_('Treść')}:\n"
        f"----------------------------------------\n"
        f"{message.content}\n"
        f"----------------------------------------\n\n"
        f"{_('Aby odpowiedzieć lub zamknąć zgłoszenie, przejdź do aplikacji')}:\n"
        f"{thread_url}\n\n"
        f"{_('Z poważaniem')},\n"
        f"{_('System Emission Impossible')}"
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        list(emails),
        fail_silently=False,
    )