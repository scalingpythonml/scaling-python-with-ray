# -*- coding: utf-8 -*-
import logging
import os

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.core.handlers import exception
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.generic import View
from django.views.i18n import JavaScriptCatalog

from ratelimit.decorators import ratelimit


logger = logging.getLogger(__name__)

handler403 = "config.errors.forbidden"
handler400 = "rest_framework.exceptions.bad_request"
handler500 = "rest_framework.exceptions.server_error"

admin.site.login = ratelimit(
    key="ip", method=ratelimit.ALL, rate="3/m", block=True
)(admin.site.login)


class IndexView(View):
    location = os.path.join(
        settings.PROJECT_PATH, os.path.join("static", "dist", "index.html")
    )

    def get(self, request):
        with open(self.location, "r") as template:
            return HttpResponse(content=template.read())


urlpatterns = [
    path("watchman/", include("watchman.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("rosetta/", include("rosetta.urls")),
    path("admin/", admin.site.urls),
    path("djstripe/", include("djstripe.urls", namespace="djstripe")),
    path("", include("apps.urls")),
    path("cms-settings/", include("cms.urls")),
    path("newsfeed/", include("newsfeed.urls", namespace="newsfeed")),
]

if settings.DEBUG or True:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

if settings.DIST:
    urlpatterns += [
        path("", cache_page(3600 * 2)(IndexView.as_view()), name="index")
    ]
