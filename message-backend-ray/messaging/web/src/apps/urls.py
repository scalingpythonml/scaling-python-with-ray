# -*- coding: utf-8 -*-
from django.urls import include, path


urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
]
