# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from apps.accounts.views import ChangePasswordView, ProfileView


app_name = "accounts"

urlpatterns = [
    path("/profile", login_required(ProfileView.as_view()), name="profile"),
    path(
        "/change-password",
        login_required(ChangePasswordView.as_view()),
        name="change-password",
    ),
]
