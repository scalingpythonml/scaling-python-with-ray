from djstripe.models import PaymentMethod, Subscription


def get_plan_info_from_subscription(subscription: Subscription):
    plan = subscription.plan
    product = plan.product

    return {
        "amount": plan.amount,
        "currency": plan.currency,
        "interval_count": plan.interval_count,
        "interval": plan.interval,
        "product_name": product.name,
        "product_description": product.description,
    }


def get_card_info_from_payment_method(payment_method: PaymentMethod):
    if payment_method.card:
        card = payment_method.card
        exp_month = (
            card["exp_month"]
            if card["exp_month"] >= 0
            else f'0{card["exp_month"]}'
        )
        exp_year = str(card["exp_year"])[:-2]
        return {
            "brand": card["brand"],
            "last4": card["last4"],
            "exp_month": exp_month,
            "exp_year": exp_year,
        }
