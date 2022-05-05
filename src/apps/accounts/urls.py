# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from apps.accounts.views import ProfileView


app_name = "accounts"

urlpatterns = [
    path("/profile", login_required(ProfileView.as_view()), name="profile")
]
