from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


from constance import config
import stripe


stripe.api_key = config.STRIPE_PRIVATE_KEY


class CheckoutSessionView(View):
    def get(self, request):
        intent = stripe.PaymentIntent.create(
            amount=4900,
            currency="usd",
            automatic_payment_methods={
                "enabled": True,
            },
        )
        return JsonResponse({"clientSecret": intent["client_secret"]})
