from django.shortcuts import render
from django.views import View

from apps.core.consts import OnboardingStepsEnum


class PaymentSuccessView(View):
    template = "payment_success.html"

    def get(self, request):
        return render(request, self.template, self.base_context)

    @property
    def base_context(self):
        return {
            "title": "Payment Success",
            "navname": "Payment Success",
            "step": OnboardingStepsEnum.ACTIVATION.value,
        }
