from django import views
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.core.consts import OnboardingStepsEnum
from apps.core.forms import PersonalInfoForm


User = get_user_model()


class PersonalInfoView(views.View):
    template = "onboarding_wizard_form.html"
    form_class = PersonalInfoForm

    def get(self, request):
        form = self.form_class()
        return render(
            request, self.template, {"form": form, **self.base_context}
        )

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.create_customer_account()
            return redirect(reverse("core:add-device"))
        return render(
            request, self.template, {"form": form, **self.base_context}
        )

    @property
    def base_context(self):
        return {
            "title": "Personal Info",
            "navname": "Personal Info",
            "action": reverse("core:personal-info"),
            "step": OnboardingStepsEnum.DETAILS.value,
        }
