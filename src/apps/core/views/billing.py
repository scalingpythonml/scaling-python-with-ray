from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from apps.core.consts import ProfileStepsEnum

from djstripe.models import Customer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.djstripe_data import (
    get_card_info_from_payment_method,
    get_plan_info_from_subscription,
)
from apps.utils.stripe import (
    add_customer_payment_method,
    delete_subscription,
    detach_payment_method,
    set_default_payment_method_for_customer,
)


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
        card = (
            get_card_info_from_payment_method(customer.default_payment_method)
            if customer.default_payment_method
            else None
        )
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
            "stripe_api_key": settings.STRIPE_TEST_PUBLIC_KEY,
            "step": ProfileStepsEnum.BILLING.value
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
                    detach_payment_method(customer.default_payment_method.id)
                add_customer_payment_method(
                    data["payment_method_id"], customer.id
                )
                set_default_payment_method_for_customer(
                    data["payment_method_id"], customer.id
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
            detach_payment_method(customer.default_payment_method.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
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
            delete_subscription(subscription.id)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
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
