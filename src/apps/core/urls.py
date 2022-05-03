from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.core.views import (
    AddDeviceView,
    IndexView,
    PersonalInfoView,
    PickPlanView,
    SignUpView,
)


app_name = "core"

urlpatterns = [
    path("index/", IndexView.as_view(), name="index"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path(
        "personal-info/",
        login_required(PersonalInfoView.as_view()),
        name="personal-info",
    ),
    path(
        "add-device",
        login_required(AddDeviceView.as_view()),
        name="add-device",
    ),
    path(
        "pick-plan", login_required(PickPlanView.as_view()), name="pick-plan"
    ),
]
