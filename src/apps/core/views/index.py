# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        #  For now backer kit
        #  return render(request, self.template_name)
        return redirect(
            "https://www.backerkit.com/call_to_action/646e79ab-f1e3-4189-a03b-18571081de4a/landing"
        )
