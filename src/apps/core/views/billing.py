from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from djstripe.models import Customer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.services.djstripe_data import get_plan_info_from_subscription
from apps.utils.get_stripe import get_stripe


stripe = get_stripe()


class BillingView(View):
    template = "billing.html"
    page_size = 10

    def get(self, request):
        customer = Customer.objects.get(id=request.user.customer_id)
        invoices = customer.invoices.all().values(
            "status", "created", "invoice_pdf"
        )
        paginator = Paginator(invoices, self.page_size)
        page = paginator.get_page(request.GET.get("page", 1))
        subscription = request.user.customer_subscription
        plan_info = (
            get_plan_info_from_subscription(subscription)
            if subscription
            else None
        )
        if customer.default_payment_method:
            dc = customer.default_payment_method.card
            card = {
                "brand": dc["brand"],
                "last4": dc["last4"],
                "exp_month": dc["exp_month"]
                if dc["exp_month"] >= 10
                else f'0{dc["exp_month"]}',
                "exp_year": str(dc["exp_year"])[-2:],
            }
        else:
            card = None
        context = {
            "page": page,
            "card": card,
            "plan": plan_info,
        }
        return render(request, self.template, {**self.base_context, **context})

    @property
    def base_context(self):
        return {
            "title": "Billing",
            "navname": "Billing",
            "stripe_api_key": settings.STRIPE_PUBLIC_KEY,
        }


class UpdatePaymentMethodSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(required=True)


class UpdatePaymentMethodAPIView(APIView):
    serializer_class = UpdatePaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        error_message = "Error"
        if serializer.is_valid():
            try:
                data = serializer.validated_data
                user = request.user
                customer = Customer.objects.get(id=user.customer_id)
                if customer.default_payment_method:
                    stripe.PaymentMethod.detach(
                        customer.default_payment_method.id
                    )
                stripe.PaymentMethod.attach(
                    data["payment_method_id"],
                    customer=user.customer_id,
                )
                stripe.Customer.modify(
                    user.customer_id,
                    invoice_settings={
                        "default_payment_method": data["payment_method_id"],
                    },
                )
                return Response({"success": True}, status=status.HTTP_200_OK)
            except Exception as e:
                if hasattr(e, "user_message"):
                    error_message = e.user_message
        return Response(
            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
        )


class DeletePaymentMethodAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        error_message = "Error"
        try:
            user = request.user
            customer = Customer.objects.get(id=user.customer_id)
            stripe.PaymentMethod.detach(customer.default_payment_method.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            if hasattr(e, "user_message"):
                error_message = e.user_message
        return Response(
            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
        )


class CancelSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        error_message = "Error"
        try:
            user = request.user
            subscription = user.customer_subscription
            stripe.Subscription.delete(subscription.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            if hasattr(e, "user_message"):
                error_message = e.user_message
        return Response(
            {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
        )


__all__ = [
    "BillingView",
    "UpdatePaymentMethodAPIView",
    "DeletePaymentMethodAPIView",
    "CancelSubscriptionAPIView",
]
