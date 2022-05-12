from django import forms
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from apps.core.models import BlockedNumber


class BlockedNumberForm(forms.Form):
    number = forms.CharField(required=True)


class BlockedNumbersView(View):
    template = "blocked_numbers.html"
    form_class = BlockedNumberForm
    page_size = 10

    def get(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        numbers = BlockedNumber.object.get_user_blocked_numbers(
            request.user
        ).values("id", "number")
        paginator = Paginator(numbers, self.page_size)
        page = paginator.get_page(request.GET.get("page", 1))
        form = self.form_class()
        return render(
            request,
            self.template,
            {**self.base_context, "page": page, "form": form, **extra_context},
        )

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            BlockedNumber.object.add_user_blocked_number(
                form.cleaned_data["number"], request.user
            )
            return self.get(request)
        return self.get(request, {"form": form, "error": True})

    @property
    def base_context(self):
        return {
            "title": "Blocked numbers",
            "navname": "Blocked numbers",
        }


class DeleteBlockedNumberView(View):
    def post(self, request, pk):
        BlockedNumber.object.delete_user_blocked_number(pk, request.user)
        return redirect(reverse("core:blocked-numbers"))


__all__ = ["DeleteBlockedNumberView", "BlockedNumbersView"]
