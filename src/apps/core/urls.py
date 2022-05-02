from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.core.views import IndexView, PersonalInfoView, SignUpView


app_name = "core"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path(
        "personal-info/",
        login_required(PersonalInfoView.as_view()),
        name="personal-info",
    ),
]
