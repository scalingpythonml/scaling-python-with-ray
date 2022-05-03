from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


from constance import config
import stripe


class CheckoutSessionView(View):
    def get(self, request):
        try:
            stripe.api_key = config.STRIPE_PRIVATE_KEY
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        "price": config.STRIPE_PRICE_ID,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                success_url=request.build_absolute_uri(
                    reverse("core:payment-success")
                ),
                cancel_url=request.build_absolute_uri(
                    reverse("core:pick-plan")
                ),
            )
            checkout_session.cancel_url += f"?session_id={checkout_session.id}"
        except Exception as e:
            print(e)
            return redirect(reverse("core:pick-plan"))

        return redirect(checkout_session.url)
