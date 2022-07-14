from django.shortcuts import render
from django.views import View

from constance import config
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.consts import OnboardingStepsEnum
from apps.utils.stripe import (
    STRIPE_PUBLIC_API_KEY,
    add_customer_payment_method,
    create_subscription,
    set_default_payment_method_for_customer,
)


class SubscriptionView(View):
    template = "subscription.html"

    def get(self, request):
        return render(request, self.template, self.base_context)

    @property
    def base_context(self):
        return {
            "title": "Subscription",
            "navname": "Subscription",
            "stripe_api_key": STRIPE_PUBLIC_API_KEY,
            "step": OnboardingStepsEnum.PAYMENT.value,
        }


class CreateSubscriptionSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(required=True)


class CreateSubscriptionAPIView(APIView):
    serializer_class = CreateSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        error_message = "Payment error. Please try again"
        if serializer.is_valid():
            try:
                data = serializer.validated_data

                customer = request.user.customer
                subscription = customer.subscriptions.filter(
                    plan__id=config.STRIPE_PRICE_ID, status="active"
                ).first()
                if subscription:
                    return Response(
                        {"error": "Subscription already exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                add_customer_payment_method(
                    data["payment_method_id"], customer.id
                )
                set_default_payment_method_for_customer(
                    data["payment_method_id"], customer.id
                )
                subscription = create_subscription(
                    config.STRIPE_PRICE_ID, customer.id
                )
                return Response(subscription, status=status.HTTP_200_OK)
            except Exception as e:
                if hasattr(e, "user_message"):
                    error_message = e.user_message
        return Response(
            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
        )


__all__ = ["SubscriptionView", "CreateSubscriptionAPIView"]
