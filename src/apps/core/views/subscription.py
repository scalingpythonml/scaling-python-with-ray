import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from constance import config
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.get_stripe import get_stripe


stripe = get_stripe()


class SubscriptionView(View):
    template = "subscription.html"

    def get(self, request):
        customer_id = request.user.customer_id
        return render(
            request,
            self.template,
            {
                **self.base_context,
                "customer_id": customer_id,
                "price_id": config.STRIPE_PRICE_ID,
            },
        )

    @property
    def base_context(self):
        return {
            "title": "Subscription",
            "navname": "Subscription",
            "stripe_api_key": settings.STRIPE_PUBLIC_KEY,
        }


class CreateSubscriptionSerializer(serializers.Serializer):
    customer_id = serializers.CharField(required=True)
    price_id = serializers.CharField(required=True)
    payment_method_id = serializers.CharField(required=True)


class CreateSubscriptionAPIView(APIView):
    serializer_class = CreateSubscriptionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        error_message = "Payment error. Please try again"
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                stripe.PaymentMethod.attach(
                    data["payment_method_id"],
                    customer=data["customer_id"],
                )
                stripe.Customer.modify(
                    data["customer_id"],
                    invoice_settings={
                        "default_payment_method": data["payment_method_id"],
                    },
                )

                subscription = stripe.Subscription.create(
                    customer=data["customer_id"],
                    items=[{"price": data["price_id"]}],
                    expand=["latest_invoice.payment_intent"],
                )
                return Response(subscription, status=status.HTTP_200_OK)
            except Exception as e:
                if hasattr(e, "user_message"):
                    error_message = e.user_message
        return Response(
            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
        )
