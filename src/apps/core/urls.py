from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from apps.core.views import *


app_name = "core"

view_urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("index_real", IndexRealView.as_view(), name="index-real"),
    path("device_lookup", DeviceLookup.as_view(), name="device-lookup"),
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
        "connect",
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
    path(
        "success-new-password/",
        auth_view.PasswordResetDoneView.as_view(
            template_name="success_chane_pass.html"
        ),
        name="success-new-password",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_view.PasswordResetConfirmView.as_view(
            template_name="new_password.html",
            success_url=reverse_lazy("core:success-new-password"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "new-password-link/",
        auth_view.PasswordResetDoneView.as_view(
            template_name="password_link.html"
        ),
        name="new-password-link",
    ),
    path(
        "forget-password/",
        auth_view.PasswordResetView.as_view(
            template_name="forget_password.html",
            email_template_name="password_reset_email.txt",
            success_url=reverse_lazy("core:new-password-link"),
        ),
        name="forget-password",
    ),
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
