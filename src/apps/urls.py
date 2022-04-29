# -*- coding: utf-8 -*-
from django.urls import include, path


urlpatterns = [path("api/accounts/", include("apps.accounts.urls"))]
