from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from apps.core.consts import OnboardingStepsEnum
from apps.core.forms import SignUpForm


User = get_user_model()


class SignUpView(View):
    template_name = "sign-up.html"
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
            return redirect(reverse("core:personal-info"))
        return render(
            request, self.template_name, {"form": form, **self.base_context}
        )

    @property
    def base_context(self):
        return {
            "title": "Sign up",
            "navname": "Get started with your account in Spacebeaver!",
            "action": reverse("core:sign-up"),
            "step": OnboardingStepsEnum.SIGN_UP.value,
        }
