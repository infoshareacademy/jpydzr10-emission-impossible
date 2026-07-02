from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from core.models import UserPageView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context["favorite_shortcuts"] = UserPageView.objects.filter(
                user=self.request.user
            ).order_by("-visit_count")[:5]
        else:
            context["favorite_shortcuts"] = None

        return context

class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"