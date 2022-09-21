# -*- coding: utf-8 -*-
import os

from django.conf import settings

import celery


# configure settings as task can access settings during execution
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
if "__ENV__" in os.environ:
    os.environ.setdefault("DJANGO_CONFIGURATION", os.environ.get("__ENV__"))

from configurations import importer  # noqa: E402 isort:skip

if not importer.installed:  # noqa: E402 isort:skip
    import configurations  # noqa: isort:skip

    configurations.setup()


app = celery.Celery(__name__)
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
