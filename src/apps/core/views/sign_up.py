from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    password_validation,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View


password_help_text = password_validation.password_validators_help_text_html()

User = get_user_model()


class SignUpForm(forms.ModelForm):
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
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm your password"}
        ),
        help_text=password_help_text,
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email_occupied = User.objects.filter(email=cleaned_data.get("email"))
        if email_occupied:
            self.add_error(
                "email", "User with this email address already exists"
            )
        if password != confirm_password:
            self.add_error("confirm_password", "Passwords does not match")
            self.add_error("confirm_password", "Passwords does not match1")

        return cleaned_data


class SignUpView(View):
    template_name = "onboarding_wizard_form.html"
    form_class = SignUpForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template_name, {"form": form, **self.base_context}
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            User.objects.create_user(email=email, password=password)
            new_user = authenticate(
                username=email,
                password=password,
            )
            login(request, new_user)
            return redirect("/")
        return render(
            request, self.template_name, {"form": form, **self.base_context}
        )

    @property
    def base_context(self):
        return {
            "title": "Sign Up",
            "navname": "Sign Up",
            "action": reverse("core:sign-up"),
        }
