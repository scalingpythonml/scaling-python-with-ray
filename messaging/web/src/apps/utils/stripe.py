from django.conf import settings

import stripe


STRIPE_PRIVATE_API_KEY = (
    settings.STRIPE_TEST_SECRET_KEY
    if settings.DEBUG
    else settings.STRIPE_LIVE_SECRET_KEY
)
STRIPE_PUBLIC_API_KEY = (
    settings.STRIPE_TEST_PUBLIC_KEY
    if settings.DEBUG
    else settings.STRIPE_LIVE_PUBLIC_KEY
)
stripe.api_key = STRIPE_PRIVATE_API_KEY


def create_customer(email: str, name: str):
    return stripe.Customer.create(email=email, name=name)


def detach_payment_method(payment_method_id: str):
    return stripe.PaymentMethod.detach(payment_method_id)


def add_customer_payment_method(payment_method_id: str, customer_id: str):
    return stripe.PaymentMethod.attach(
        payment_method_id,
        customer=customer_id,
    )


def set_default_payment_method_for_customer(
    payment_method_id: str, customer_id: str
):
    return stripe.Customer.modify(
        customer_id,
        invoice_settings={
            "default_payment_method": payment_method_id,
        },
    )


def create_subscription(price_id: str, customer_id: str):
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        expand=["latest_invoice.payment_intent"],
    )


def delete_subscription(subscription_id: str):
    return stripe.Subscription.delete(subscription_id)
