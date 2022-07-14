from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import render
from django.urls import reverse

from apps.core.forms import LoginForm


User = get_user_model()


def login_routing(user: User):
    """
    Select page based on profile status
    """
    if user.have_any_subscription:
        return reverse("core:dashboard")
    user = User.objects.onboarding_complete_annotate(id=user.id).first()
    if not user.have_personal_info:
        return reverse("core:personal-info")
    if not user.user_have_device:
        return reverse("core:add-device")
    return reverse("core:pick-plan")


class LoginView(BaseLoginView):
    template_name = "login.html" 
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template_name, {"form": form}
        )

    def get_success_url(self):
        return login_routing(self.request.user)
