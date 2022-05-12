from django.shortcuts import render
from django.views import View

from constance import config


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
            "image": f"/media/{config.IMAGE}",
            "description": config.DESCRIPTION,
            "price": config.PRICE,
            "step": 4,
        }
