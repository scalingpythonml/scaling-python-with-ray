from django.views import View
from django.shortcuts import render

from apps.core.forms import ForgetPasswordForm

class ForgetPasswordView(View):
    template_name = "forget_password.html"
    form_class = ForgetPasswordForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})




