from django.views import View
from django.shortcuts import render

from apps.core.forms import NewPasswordForm

class SuccessNewPasswordView(View):
    template_name = "success_chane_pass.html"

    def get(self, request):
        return render(request, self.template_name)




