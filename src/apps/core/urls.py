from django.contrib.auth.decorators import login_required
from django.urls import path

from apps.core.views import *


app_name = "core"

view_urlpatterns = [
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
        "payment-success",
        login_required(PaymentSuccessView.as_view()),
        name="payment-success",
    ),
    path("login", LoginView.as_view(), name="login"),
    path(
        "replace-device",
        login_required(ReplaceDeviceView.as_view()),
        name="replace-device",
    ),
    path(
        "dashboard", login_required(DashboardView.as_view()), name="dashboard"
    ),
    path(
        "subscription",
        login_required(SubscriptionView.as_view()),
        name="subscription",
    ),
    path("billing", login_required(BillingView.as_view()), name="billing"),
    path(
        "blocked-numbers",
        login_required(BlockedNumbersView.as_view()),
        name="blocked-numbers",
    ),
    path(
        "delete-blocked-number/<int:pk>",
        login_required(DeleteBlockedNumberView.as_view()),
        name="delete-blocked-number",
    ),
    path("forget-password", ForgetPasswordView.as_view(), name="forget-password"),
    path("new-password", NewPasswordView.as_view(), name="new-password"),
    path("success-new-password", SuccessNewPasswordView.as_view(), name="success-new-password"),
    path("new-password-link", NewPasswordView.as_view(), name="new-password-link"),
]

api_urlpatterns = [
    path(
        "create-subscription",
        login_required(CreateSubscriptionAPIView.as_view()),
    ),
    path("update-payment-method", UpdatePaymentMethodAPIView.as_view()),
    path("delete-payment-method", DeletePaymentMethodAPIView.as_view()),
    path("cancel-subscription", CancelSubscriptionAPIView.as_view()),
    path("device-owner", DeviceOwnerApiView.as_view()),
]

urlpatterns = view_urlpatterns + api_urlpatterns
