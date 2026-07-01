from accounts.models import CustomUser
from companies.models import Companies
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import MessageReplyForm, ThreadCreateForm
from .models import Message, Thread
from .send_mail import (
    send_thread_notification,
)


class ThreadListView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = "communications/thread_list.html"
    context_object_name = "threads"
    paginate_by = 15

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or getattr(user, "role", None) == "admin":
            qs = Thread.objects.all()
        else:
            user_company_ids = user.company_permissions.filter(
                can_read=True
            ).values_list("company_id", flat=True)
            qs = Thread.objects.filter(
                Q(author=user) | Q(company_id__in=user_company_ids)
            ).distinct()

        company_filter = self.request.GET.get("company")
        author_filter = self.request.GET.get("author")
        status_filter = self.request.GET.get("status")
        query_filter = self.request.GET.get("q")

        if company_filter:
            qs = qs.filter(company_id=company_filter)
        if author_filter:
            qs = qs.filter(author_id=author_filter)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if query_filter:
            qs = qs.filter(subject__icontains=query_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_superuser or getattr(user, "role", None) == "admin":
            context["available_companies"] = Companies.objects.all()
            context["available_authors"] = CustomUser.objects.all()
        else:
            user_company_ids = user.company_permissions.filter(
                can_read=True
            ).values_list("company_id", flat=True)
            context["available_companies"] = Companies.objects.filter(
                id__in=user_company_ids
            )
            context["available_authors"] = CustomUser.objects.filter(
                created_threads__company_id__in=user_company_ids
            ).distinct()

        context["filters"] = self.request.GET
        return context


class ThreadDetailView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = "communications/thread_detail.html"
    context_object_name = "thread"

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or getattr(user, "role", None) == "admin":
            return Thread.objects.all()

        user_company_ids = user.company_permissions.filter(can_read=True).values_list(
            "company_id", flat=True
        )
        return Thread.objects.filter(
            Q(author=user) | Q(company_id__in=user_company_ids)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reply_form"] = MessageReplyForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.status == "closed":
            messages.error(
                request, "Nie można dodawać wiadomości do zamkniętego wątku."
            )
            return redirect("communications:thread_detail", pk=self.object.pk)

        form = MessageReplyForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.thread = self.object
            msg.sender = request.user
            msg.save()
            send_thread_notification(request, self.object, msg, is_new=False)

            messages.success(request, "Odpowiedź została wysłana.")
            return redirect("communications:thread_detail", pk=self.object.pk)

        return self.render_to_response(self.get_context_data(reply_form=form))


class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = ThreadCreateForm
    template_name = "communications/thread_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        thread = form.save(commit=False)
        thread.author = self.request.user
        thread.save()
        first_msg = Message.objects.create(
            thread=thread,
            sender=self.request.user,
            content=form.cleaned_data["first_message"],
        )

        send_thread_notification(self.request, thread, first_msg, is_new=True)

        messages.success(self.request, "Zgłoszenie zostało pomyślnie utworzone.")
        return redirect("communications:thread_detail", pk=thread.pk)


class ThreadCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        thread = get_object_or_404(Thread, pk=pk)

        if (
            thread.author == request.user
            or request.user.is_superuser
            or getattr(request.user, "role", None) == "admin"
        ):
            thread.status = "closed"
            thread.save()
            messages.success(request, "Wątek został pomyślnie zamknięty.")
        else:
            messages.error(request, "Nie masz uprawnień do zamknięcia tego wątku.")

        return redirect("communications:thread_detail", pk=pk)
