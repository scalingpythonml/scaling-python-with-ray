from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from djstripe.models import Customer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
        dc = customer.default_payment_method.card
        paginator = Paginator(invoices, self.page_size)
        page = paginator.get_page(request.GET.get("page", 1))
        card = {
            "brand": dc["brand"],
            "last4": dc["last4"],
            "exp_month": dc["exp_month"]
            if dc["exp_month"] >= 10
            else f'0{dc["exp_month"]}',
            "exp_year": str(dc["exp_year"])[-2:],
        }
        context = {
            "page": page,
            "card": card,
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
