from django.shortcuts import render
from django.views import View

from constance import config


class PickPlanView(View):
    template = "pick_plan.html"

    def get(self, request):
        context = {
            "title": config.TITLE,
            "image": f"/media/{config.IMAGE}",
            "description": config.DESCRIPTION,
            "price": config.PRICE,
        }
        return render(request, self.template, context)
