# -*- coding: utf-8 -*-
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import include, path, reverse

from apps.accounts.views import (
    ChangeEmailView,
    ChangePasswordView,
    ProfileView,
)


app_name = "accounts"

urlpatterns = [
    path("profile", login_required(ProfileView.as_view()), name="profile"),
    path(
        "change-password",
        login_required(ChangePasswordView.as_view()),
        name="change-password",
    ),
    path(
        "change-email",
        login_required(ChangeEmailView.as_view()),
        name="change-email",
    ),
    path("logout", LogoutView.as_view(next_page="/"), name="logout"),
]
