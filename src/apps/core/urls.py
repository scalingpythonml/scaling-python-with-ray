from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.core.views import (
    AddDeviceView,
    CheckoutSessionView,
    IndexView,
    LoginView,
    PaymentFormView,
    PaymentSuccessView,
    PersonalInfoView,
    PickPlanView,
    ReplaceDeviceView,
    SignUpView,
)


app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
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
    path(
        "checkout-session",
        login_required(CheckoutSessionView.as_view()),
        name="checkout-session",
    ),
    path(
        "payment-success",
        login_required(PaymentSuccessView.as_view()),
        name="payment-success",
    ),
    path(
        "payment-form",
        login_required(PaymentFormView.as_view()),
        name="payment-form",
    ),
    path("login", LoginView.as_view(), name="login"),
    path(
        "replace-device",
        login_required(ReplaceDeviceView.as_view()),
        name="replace-device",
    ),
]
