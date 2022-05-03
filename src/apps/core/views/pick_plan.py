import copy

from django.shortcuts import render
from django.urls import reverse
from django.views import View


from constance import config
import stripe


class PickPlanView(View):
    template = "pick_plan.html"

    def get(self, request):
        context = copy.deepcopy(self.base_context)

        return render(request, self.template, context)

    @property
    def base_context(self):
        return {
            "title": config.TITLE,
            "image": f"/media/{config.IMAGE}",
            "description": config.DESCRIPTION,
            "price": config.PRICE,
        }
