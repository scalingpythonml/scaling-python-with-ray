from django.conf import settings
from django.shortcuts import render
from django.views import View

from constance import config

from apps.core.consts import OnboardingStepsEnum


class PickPlanView(View):
    template = "pick_plan.html"

    def get(self, request):
        return render(request, self.template, self.base_context)

    @property
    def base_context(self):
        return {
            "title": "Pick Plan",
            "navname": "Pick Plan",
            "plan_title": config.TITLE,
            "image": f"{settings.MEDIA_URL}{config.IMAGE}",
            "description": config.DESCRIPTION,
            "price": config.PRICE,
            "step": OnboardingStepsEnum.PICK_PLAN.value,
        }
