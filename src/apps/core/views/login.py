from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View


User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Enter your email"}),
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter your password"}
        ),
        required=True,
    )


def login_routing(user: User):
    user = User.objects.onboarding_complete_annotate(id=user.id).first()
    if not user.have_personal_info:
        return redirect(reverse("core:personal-info"))
    if not user.user_have_device:
        return redirect(reverse("core:add-device"))
    if not user.complete_onboarding:
        return redirect(reverse("core:pick-plan"))
    return redirect(reverse("core:index"))


class LoginView(View):
    template = "login.html"
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            if user:
                return login_routing(user)
            else:
                form.add_error(None, "Invalid credentials")
        return render(
            request,
            self.template,
            {"form": form, "action": reverse("core:login")},
        )
