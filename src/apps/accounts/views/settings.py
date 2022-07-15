from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from apps.core.consts import ProfileStepsEnum


User = get_user_model()


class SettingsForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Type your email"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
    )
    class Meta:
        model = User
        fields = [
            "email",
            "password"
        ]


class SettingsView(View):
    template_name = "accounts_form.html"
    form_class = SettingsForm
    
    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template_name, {**self.base_context, "form": form}
        )
   
    @property
    def base_context(self):
        return {
            "title": "Settings",
            "navname": "Settings",
            "action": reverse("accounts:profile"),
            "action_button_name": "Save",
            "step": ProfileStepsEnum.SETTINGS.value,
        }
