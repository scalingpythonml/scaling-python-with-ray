from django.views import View
from django.shortcuts import render

from apps.core.forms import NewPasswordForm

class PasswordLinkView(View):
    template_name = "new_password.html"

    def get(self, request):
        return render(request, self.template_name)




