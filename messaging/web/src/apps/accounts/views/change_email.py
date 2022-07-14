from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from templated_email import send_templated_mail

from apps.accounts.forms import ChangeEmailForm


class ChangeEmailView(View):
    template = "accounts_form.html"
    form_class = ChangeEmailForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data["new_email"]
            user.save()
            send_templated_mail(
                "change_email_notification",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                {},
            )

            return self.get(request)
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    @property
    def base_context(self):
        return {
            "title": "Change email",
            "navname": "Change email",
            "action": reverse("accounts:change-email"),
            "action_button_name": "Update",
        }
