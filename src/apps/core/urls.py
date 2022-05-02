from django.urls import path

from apps.core.views import IndexView, SignUpView


app_name = "core"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
]
