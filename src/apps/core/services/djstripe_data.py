from djstripe.models import Subscription


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
