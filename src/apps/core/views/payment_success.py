from django.shortcuts import render
from django.views import View


class PaymentSuccessView(View):
    template = "payment_success.html"

    def get(self, request):
        # TODO: truth logic
        if not request.user.complete_onboarding:
            request.user.complete_onboarding = True
            request.user.save()
        return render(request, self.template, {"step": 6})
