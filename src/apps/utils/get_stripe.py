def get_stripe():
    import stripe
    from constance import config

    stripe.api_key = config.STRIPE_PRIVATE_KEY
    return stripe
