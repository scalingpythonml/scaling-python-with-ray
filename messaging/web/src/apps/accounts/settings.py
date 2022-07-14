import datetime
from types import SimpleNamespace

from django.conf import settings


DEFAULT_SETTINGS = {"JWT_ALGORITHM": "HS256"}

app_settings = SimpleNamespace(
    **dict(DEFAULT_SETTINGS, **getattr(settings, "ACCOUNTS", {}))
)
