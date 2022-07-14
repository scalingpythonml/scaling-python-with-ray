from django.views import View
from django.shortcuts import render

class NewPasswordView(View):
    template_name = "password_link.html"

    def get(self, request):
        return render(request, self.template_name)
