# -*- coding: utf-8 -*-
from configurations import Configuration

from .common import Settings


class Test(Settings, Configuration):
    DEBUG = False
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
    DRF_RECAPTCHA_TEST = True

    @property
    def CORS_ORIGIN_REGEX_WHITELIST(self):
        return [r"^.*localhost.*$", "^.*0.0.0.0.*$", "^.*127.0.0.1.*$"]

    @property
    def CACHES(self):
        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": self._CACHE_NETLOC,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "PARSER_CLASS": "redis.connection.HiredisParser",
                    "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                    "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
                    "IGNORE_EXCEPTIONS": True,
                },
            }
        }

    TEST_RUNNER = "django.test.runner.DiscoverRunner"
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

    @property
    def LOGGING(self):
        level = "DEBUG"
        return self._update_logging(
            super().LOGGING, level=level, formater="verbose", handler="console"
        )
