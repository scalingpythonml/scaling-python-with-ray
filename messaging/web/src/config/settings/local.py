# -*- coding: utf-8 -*-
from configurations import Configuration

from .common import Settings


class Local(Settings, Configuration):
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
    CELERY_TASK_ALWAYS_EAGER = True
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

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
                    "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
                    "IGNORE_EXCEPTIONS": True,
                },
            }
        }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"

    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ["django_extensions"]

    @property
    def LOGGING(self):
        level = "DEBUG"
        return self._update_logging(
            super().LOGGING, level=level, formater="verbose", handler="console"
        )

    @property
    def TEMPLATES(self):
        TEMPLATES = super().TEMPLATES
        TEMPLATES[0]["OPTIONS"].update({"debug": self.DEBUG})
        return TEMPLATES
