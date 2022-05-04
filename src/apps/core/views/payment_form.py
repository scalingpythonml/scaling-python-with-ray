from django.shortcuts import render
from django.urls import reverse
from django.views import View


from constance import config
import stripe


stripe.api_key = config.STRIPE_PRIVATE_KEY


class PaymentFormView(View):
    template = "payment_form.html"

    def get(self, request):
        context = {
            "stripe_key": config.STRIPE_PUBLIC_KEY,
            "success_url": request.build_absolute_uri(
                reverse("core:payment-success")
            ),
        }
        return render(request, self.template, context)
