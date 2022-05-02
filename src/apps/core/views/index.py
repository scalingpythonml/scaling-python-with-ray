# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


class IndexView(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name)
