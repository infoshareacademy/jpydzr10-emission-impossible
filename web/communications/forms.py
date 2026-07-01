from django import forms

from .models import Message, Thread


class ThreadCreateForm(forms.ModelForm):
    first_message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "class": "w-full bg-[rgba(255,255,255,0.06)] border border-border-subtle rounded-xl text-text-main p-3 focus:outline-none focus:border-accent font-mono text-sm",
            }
        ),
        label="Treść wiadomości",
    )

    class Meta:
        model = Thread
        fields = ["company", "category", "subject"]
        widgets = {
            "company": forms.Select(
                attrs={
                    "class": "w-full bg-[rgba(255,255,255,0.06)] border border-border-subtle rounded-xl text-text-main p-3 focus:outline-none focus:border-accent font-mono text-sm"
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full bg-[rgba(255,255,255,0.06)] border border-border-subtle rounded-xl text-text-main p-3 focus:outline-none focus:border-accent font-mono text-sm"
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "w-full bg-[rgba(255,255,255,0.06)] border border-border-subtle rounded-xl text-text-main p-3 focus:outline-none focus:border-accent font-mono text-sm"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # Użytkownik może utworzyć wątek tylko dla spółek, do których ma dostęp
            from companies.models import Companies

            user_companies = user.company_permissions.filter(can_read=True).values_list(
                "company", flat=True
            )
            self.fields["company"].queryset = Companies.objects.filter(
                id__in=user_companies
            )


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Napisz odpowiedź...",
                    "class": "w-full bg-[rgba(255,255,255,0.06)] border border-border-subtle rounded-xl text-text-main p-3 focus:outline-none focus:border-accent font-mono text-sm",
                }
            ),
        }
