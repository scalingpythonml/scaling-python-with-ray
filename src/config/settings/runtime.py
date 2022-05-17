# -*- coding: utf-8 -*-
import os


from configurations import Configuration
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .common import Settings


if os.environ.get("SENTRY_ENDPOINT"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_ENDPOINT"),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=os.environ.get("ENVIRONMENT"),
        send_default_pii=True,
    )


class Runtime(Settings, Configuration):
    DIST = True
    DEBUG = False
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    X_FRAME_OPTIONS = "SAMEORIGIN"
    USE_X_FORWARDED_HOST = True

    AWS_PRELOAD_METADATA = True
    AWS_HEADERS = {
        "Expires": "Thu, 31 Dec 2099 20:00:00 GMT",
        "Cache-Control": "max-age=94608000",
    }

    def _get_env_vars(self):
        return [
            "ENVIRONMENT",
            "SECRET_KEY",
            "SSL",
            "DOMAIN",
            "CACHE_NETLOC",
            "DATA_NETLOC",
            "BROKER_NETLOC",
            "STATIC_URL",
            "MEDIA_URL",
            "AWS_REGION",
            "AWS_S3_HOST",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_STORAGE_BUCKET_NAME",
            "AWS_S3_SECURE_URLS",
            "AWS_STATIC_LOCATION",
            "AWS_MEDIA_LOCATION",
            "OUTSIDE_DATA_NETLOC",
            "STRIPE_LIVE_SECRET_KEY",
            "STRIPE_TEST_SECRET_KEY",
            "STRIPE_LIVE_PUBLIC_KEY",
            "STRIPE_TEST_PUBLIC_KEY",
            "DJSTRIPE_WEBHOOK_SECRET",
        ]

    @property
    def CORS_ORIGIN_REGEX_WHITELIST(self):
        proto = f"{self.PROTO}://"
        prefix = rf"{proto}(.*\.)?"
        segment = rf"{self.DOMAIN_URL.replace(proto, prefix)}"
        suffix = self.DOMAIN.split(".")[-1]
        return [rf"^{segment}\.{suffix}$"]

    @property
    def s3_region_name(self):
        return self._AWS_REGION

    @property
    def s3_region_endpoint(self):
        return self._AWS_S3_HOST

    # setup AWS as files & static storage
    @property
    def AWS_MEDIA_BUCKET(self):
        return self._AWS_STORAGE_BUCKET_NAME

    @property
    def AWS_STATIC_BUCKET(self):
        return self._AWS_STORAGE_BUCKET_NAME

    @property
    def AWS_STATIC_LOCATION(self):
        return self._AWS_STATIC_LOCATION

    @property
    def AWS_MEDIA_LOCATION(self):
        return self._AWS_MEDIA_LOCATION

    STATICFILES_STORAGE = "config.storages.AWSStaticStorage"
    DEFAULT_FILE_STORAGE = "config.storages.AWSMediaStorage"
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

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
                    "PICKLE_VERSION": -1,
                    "IGNORE_EXCEPTIONS": False,
                },
            }
        }

    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
    SESSION_CACHE_ALIAS = "default"
    SELECT2_CACHE_PREFIX = "default"

    @property
    def ALLOWED_HOSTS(self):
        return super(Runtime, self).ALLOWED_HOSTS() + ["app"]

    @property
    def INSTALLED_APPS(self):
        base_apps = super().INSTALLED_APPS
        base_apps.insert(
            base_apps.index("django.contrib.staticfiles"), "collectfast"
        )
        return base_apps

    COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"

    @property
    def LOGGING(self):
        level = "ERROR"
        return self._update_logging(
            super().LOGGING,
            level=level,
            formater="default",
            handler=["stdout", "stderr"],
        )
