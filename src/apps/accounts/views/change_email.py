from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from templated_email import send_templated_mail


User = get_user_model()


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Enter new email"})
    )

    def clean(self):
        cleaned_data = super(ChangeEmailForm, self).clean()
        email_occupied = User.objects.filter(email=cleaned_data["new_email"])
        if email_occupied:
            self.add_error("new_email", "User with this email exist")

        return cleaned_data


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
            "title": "Change password",
            "navname": "Change password",
            "action": reverse("accounts:change-email"),
            "action_button_name": "Update",
        }
