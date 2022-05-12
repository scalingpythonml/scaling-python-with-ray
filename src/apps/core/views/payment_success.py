from django.shortcuts import render
from django.views import View


class PaymentSuccessView(View):
    template = "payment_success.html"

    def get(self, request):
        return render(request, self.template, {"step": 6})
