from accounts.models import CustomUser
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_thread_notification(request, thread, message, is_new=False):
    """
    Wysyła powiadomienie e-mail o nowym wątku lub nowej wiadomości.
    Odbiorcy: Uczestnicy wątku + osoby ze statusem can_save dla danej spółki.
    """
    # Znajdź osoby, które mogą edytować (can_save) dla danej spółki
    save_users = CustomUser.objects.filter(
        company_permissions__company=thread.company, company_permissions__can_save=True
    )

    # Wszyscy uczestnicy dotychczasowi w wątku
    participant_ids = thread.messages.values_list("sender_id", flat=True).distinct()
    participants = CustomUser.objects.filter(id__in=participant_ids)

    # Zbuduj unikalny zbiór adresów e-mail (bez nadawcy, żeby nie dostawał własnych maili)
    emails = set()
    for u in save_users.union(participants):
        if u.email and u != message.sender:
            emails.add(u.email)

    if not emails:
        return  # Brak odbiorców

    thread_url = request.build_absolute_uri(
        reverse("communications:thread_detail", args=[thread.id])
    )

    akcja = "Nowe zgłoszenie" if is_new else "Nowa odpowiedź"
    subject = f"[Emission Impossible] {akcja}: {thread.subject} - {thread.company.name}"

    body = (
        f"Szanowni Państwo,\n\n"
        f"Użytkownik {message.sender.username} dodał nową wiadomość w wątku dotyczącym spółki {thread.company.name}.\n\n"
        f"Kategoria: {thread.get_category_display()}\n"
        f"Treść:\n"
        f"----------------------------------------\n"
        f"{message.content}\n"
        f"----------------------------------------\n\n"
        f"Aby odpowiedzieć lub zamknąć zgłoszenie, przejdź do aplikacji:\n"
        f"{thread_url}\n\n"
        f"Z poważaniem,\nSystem Emission Impossible"
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        list(emails),
        fail_silently=False,
    )
