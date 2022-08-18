from django import views
from django.shortcuts import render


def my_error404(request, exception):
    return render(request, "404.html")
