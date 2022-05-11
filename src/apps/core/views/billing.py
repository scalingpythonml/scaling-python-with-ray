from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from djstripe.models import Customer


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
        }
