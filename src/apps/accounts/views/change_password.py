from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from templated_email import send_templated_mail

from apps.accounts.forms import ChangePasswordForm


class ChangePasswordView(View):
    template = "accounts_form.html"
    form_class = ChangePasswordForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        user = request.user
        if form.is_valid():
            valid_password = user.check_password(
                form.cleaned_data["old_password"]
            )
            if valid_password:
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                user = authenticate(
                    username=user.email,
                    password=form.cleaned_data["new_password"],
                )
                login(request, user)
                send_templated_mail(
                    "change_password_notification",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    {},
                )
                return self.get(request)
            form.add_error("old_password", "Invalid password")
        return render(
            request, self.template, {**self.base_context, "form": form}
        )

    @property
    def base_context(self):
        return {
            "title": "Change password",
            "navname": "Change password",
            "action": reverse("accounts:change-password"),
            "action_button_name": "Update",
        }
