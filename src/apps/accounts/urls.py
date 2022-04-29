# -*- coding: utf-8 -*-
from django.urls import include, path

from rest_framework.routers import DefaultRouter


app_name = "accounts"

router = DefaultRouter()
urlpatterns = []

urlpatterns += router.urls
