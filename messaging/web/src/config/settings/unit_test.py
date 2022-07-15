# -*- coding: utf-8 -*-
import os
from configurations import Configuration

from .common import Settings


class UnitTest(Settings, Configuration):
    DEBUG = False
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
    DRF_RECAPTCHA_TEST = True

    @property
    def CORS_ORIGIN_REGEX_WHITELIST(self):
        return [r"^.*localhost.*$", "^.*0.0.0.0.*$", "^.*127.0.0.1.*$"]

    TEST_RUNNER = "django.test.runner.DiscoverRunner"
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

    @property
    def LOGGING(self):
        level = "DEBUG"
        return self._update_logging(
            super().LOGGING, level=level, formater="verbose", handler="console"
        )

    @property
    def DATABASES(self):
        engine = 'django.db.backends.sqlite3'
        return {
            "default": {
                "NAME": os.path.join(BASE_DIR, "unit_farts.db").as_posix,
                }
            }
