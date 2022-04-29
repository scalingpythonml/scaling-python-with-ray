# -*- coding: utf-8 -*-
import os
import socket
import sys
import urllib.parse
import warnings

from kombu import Exchange, Queue


gettext = lambda s: s  # noqa

warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)


class Settings:
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        """ Run environment variables check before start """
        red, bold, end = "\033[91m", "\033[1m", "\033[0m"

        if not os.environ.get("__ENV__"):
            info = "__ENV__ variable is not defined."
            sys.stdout.write("{}{}{}{}\n".format(red, bold, info, end))
            sys.exit(-1)

        environment = self._get_env_vars()

        def rs(path):
            with open(path, "r") as f:
                return f.read().replace("\n", "").strip()

        mv = []

        for e in environment:
            key = e
            val = os.environ.get(key)
            if not val:
                key = f"{e}_FILE"
                val = os.environ.get(key)
                if val:
                    val = rs(os.environ.get(key))

            if not val:
                mv.append(key)
            else:
                setattr(self, "_%s" % e, val)

        if mv:
            msg_map = ""
            for e in mv:
                msg_map += "{}: {},\n ".format(e, os.environ.get(e))
            info = (
                "Environment configuration error. Some of next "
                + "variables is not defined:\n {}."
            ).format(msg_map)

            sys.stdout.write("{}{}{}{}\n".format(red, bold, info, end))
            sys.exit(-1)

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
        ]

    # INSTANCE CONFIGURATION
    # =======================================================================
    SITE_ID = 1
    WSGI_APPLICATION = "config.wsgi.application"
    DIST = False

    # URL CONFIGURATION
    # =======================================================================
    @property
    def USE_HTTPS(self):
        return self._SSL == "on"

    @property
    def DOMAIN(self):
        return self._DOMAIN

    @property
    def DOMAIN_NAME(self):
        return self.DOMAIN

    @property
    def PROTO(self):
        return "http" if not self.USE_HTTPS else "https"

    @property
    def DOMAIN_URL(self):
        return f"{self.PROTO}://{self.DOMAIN}"

    ROOT_URLCONF = "config.urls"

    # PATH CONFIGURATION
    # =======================================================================
    CONFIG_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )

    PROJECT_PATH = os.path.abspath(os.path.join(CONFIG_PATH, os.pardir))

    TEMP_PATH = os.path.abspath(os.path.join(PROJECT_PATH, "tmp"))

    # HOST CONFIGURATION
    # =======================================================================
    @property
    def ALLOWED_HOSTS(self):
        return ["localhost", "127.0.0.1", "0.0.0.0", self.DOMAIN]

    @property
    def INTERNAL_IPS(self):
        return [
            "localhost",
            "127.0.0.1",
            "10.0.2.2",
            self.DOMAIN,
            socket.gethostbyname(socket.gethostname())[:-1] + "1",
        ]

    @property
    def SECRET_KEY(self):
        return self._SECRET_KEY

    # MIDDLEWARE CONFIGURATION
    # =======================================================================
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    # DEBUG
    # =======================================================================
    DEBUG = False

    # FIXTURE CONFIGURATION
    # =======================================================================
    FIXTURE_DIRS = (os.path.abspath(os.path.join(PROJECT_PATH, "fixtures")),)

    # DATABASE CONFIGURATION
    # =======================================================================
    @property
    def DATABASES(self):
        engine = "django.db.backends.postgresql"
        config = urllib.parse.urlparse(self._DATA_NETLOC)
        return {
            "default": {
                "ENGINE": engine,
                "NAME": config.path[1:],
                "USER": config.username,
                "PASSWORD": config.password,
                "HOST": config.hostname,
                "PORT": config.port,
                "ATOMIC_REQUESTS": True,
                "CONN_MAX_AGE": 0,  # closing the database connection at
                # the end of each request
            }
        }

    # CACHING
    # =======================================================================
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
            "LOCATION": "",
        }
    }

    # GENERAL CONFIGURATION
    # =======================================================================
    TIME_ZONE = "UTC"

    # I18N CONFIGURATION
    # =======================================================================
    LANGUAGE_CODE = "en"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LANGUAGES = (("en", gettext("English")),)

    LOCALE_PATHS = (os.path.join(PROJECT_PATH, "locale"),)

    # TEMPLATE CONFIGURATION
    # =======================================================================
    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
            "DIRS": [],
            "OPTIONS": {
                "debug": DEBUG,
                "loaders": [
                    (
                        "django.template.loaders.cached.Loader",
                        [
                            "django.template.loaders.filesystem.Loader",
                            "django.template.loaders.app_directories.Loader",
                        ],
                    )
                ],
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.contrib.messages.context_processors.messages",
                ],
                "libraries": {},
                "builtins": [
                    "django.templatetags.i18n",
                    "django.templatetags.l10n",
                    "django.templatetags.static",
                ],
            },
        }
    ]

    # STATIC & MEDIA FILE CONFIGURATION
    # =======================================================================
    PUBLIC_ROOT = os.path.join(PROJECT_PATH, "public")
    # STATIC CONFIGURATION
    # -----------------------------------------------------------------------
    @property
    def STATIC_URL(self):
        return self._STATIC_URL

    STATIC_ROOT = os.path.join(PUBLIC_ROOT, "static")
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )
    STATICFILES_DIRS = (os.path.join(PROJECT_PATH, "static"),)
    # MEDIA CONFIGURATION
    # -----------------------------------------------------------------------
    @property
    def MEDIA_URL(self):
        return self._MEDIA_URL

    MEDIA_ROOT = os.path.join(PUBLIC_ROOT, "media")

    # PASSWORD VALIDATION
    # =======================================================================

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
        },
    ]

    # AUTHENTICATION CONFIGURATION
    # =======================================================================
    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "apps.accounts.auth.backends.EmailBackend",
    )

    # APP CONFIGURATION
    # =======================================================================
    # FRAMEWORK CONFIGURATION
    # -----------------------------------------------------------------------
    FRAMEWORK = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "django.contrib.admin",
    ]

    # MESSAGES
    # ~~~~~~~~~~~~~~~~
    FRAMEWORK += ["django.contrib.messages"]
    MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

    # LIBRARIES CONFIGURATION
    # -----------------------------------------------------------------------
    LIBS = ["configurations"]

    # ROSETTA
    # ~~~~~~~~
    LIBS += ["rosetta"]
    ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True

    # SORL.THUMBNAIL
    # ~~~~~~~~~~~~~~~~
    LIBS += ["sorl.thumbnail"]
    TEMPLATES[0]["OPTIONS"]["libraries"].update(
        {"sorl_thumbnail": "sorl.thumbnail.templatetags.thumbnail"}
    )

    # REST FRAMEWORK
    # ~~~~~~~~~~~~~~
    LIBS += ["rest_framework", "rest_framework_filters"]
    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": (
            "rest_framework.permissions.IsAuthenticated",
        ),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ),
        "DEFAULT_THROTTLE_RATES": {},
    }

    # WATCHMAN
    # ~~~~~~
    LIBS += ["watchman"]

    # STORAGES
    # ~~~~~~~~
    LIBS += ["storages"]
    AWS_DEFAULT_ACL = None

    # CORESHEADERS
    # ~~~~~~~~~~~~
    LIBS += ["corsheaders"]
    MIDDLEWARE.insert(1, "corsheaders.middleware.CorsMiddleware")
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_HEADERS = (
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "contentdisposition",
    )

    CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]

    @property
    def CORS_ORIGIN_REGEX_WHITELIST(self):
        raise NotImplementedError()

    CORS_EXPOSE_HEADERS = ("accept", "origin", "content-type")

    # MAIL (TEMPLATED EMAIL, CELERY EMAIL)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @property
    def DEFAULT_FROM_EMAIL(self):
        return "noreply@server.local"

    @property
    def SERVER_EMAIL(self):
        return self.DEFAULT_FROM_EMAIL

    EMAIL_SUBJECT_PREFIX = ""

    # TEMPLATED EMAIL
    LIBS += ["templated_email"]

    @property
    def TEMPLATED_EMAIL_FROM_EMAIL(self):
        return self.DEFAULT_FROM_EMAIL

    TEMPLATED_EMAIL_AUTO_PLAIN = False
    TEMPLATED_EMAIL_TEMPLATE_DIR = "emails/"
    TEMPLATED_EMAIL_FILE_EXTENSION = "email"

    # CELERY EMAIL
    LIBS += ["djcelery_email"]

    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
    CELERY_EMAIL_TASK_CONFIG = {
        "queue": "transient",
        "name": "celery_email_send",
        "ignore_result": False,
        "rate_limit": "50/m",
    }

    # CELERY
    # ~~~~~~
    LIBS += ["django_celery_beat"]

    @property
    def CELERY_BROKER_URL(self):
        return self._BROKER_NETLOC

    @property
    def CELERY_RESULT_BACKEND(self):
        return self._CACHE_NETLOC

    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = True  # only with TIME_ZONE = 'UTC'
    CELERY_TASK_IGNORE_RESULT = False
    CELERY_RESULT_EXPIRES = 24 * 3600  # Expire results after 24h
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_WORKER_MAX_TASKS_PER_CHILD = (
        4  # After handling 4 tasks, a worker should restart
    )
    CELERY_TASK_QUEUES = (
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("transient", Exchange("transient"), routing_key="transient"),
    )
    CELERY_TASK_DEFAULT_QUEUE = CELERY_TASK_DEFAULT_EXCHANGE = "default"
    CELERY_TASK_DEFAULT_ROUTING_KEY = CELERY_TASK_DEFAULT_QUEUE
    CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
    CELERY_TASK_DEFAULT_DELIVERY_MODE = "persistent"

    # APPS CONFIGURATION
    # -----------------------------------------------------------------------

    APPS = ["apps.utils.apps.Config"]

    # ACCOUNTS
    # ~~~~~~~~~
    APPS += ["apps.accounts.apps.Config"]

    AUTH_USER_MODEL = "accounts.User"

    # -----------------------------------------------------------------------
    INSTALLED_APPS = FRAMEWORK + LIBS + APPS
    # -----------------------------------------------------------------------

    # LOGGING CONFIGURATION
    # =======================================================================
    ADMINS = []
    MANAGERS = ADMINS

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s"
            },
            "verbose": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s"
            },
            "file": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s"
            },
        },
        "filters": {
            "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse"
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "stderr": {
                "level": "ERROR",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stderr,
            },
            "stdout": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "null": {"class": "logging.NullHandler"},
        },
        "loggers": {
            "django": {
                "level": "ERROR",
                "handlers": ["stderr"],
                "propagate": False,
            },
            "django.request": {
                "handlers": ["stderr"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.template": {"handlers": ["null"], "propagate": False},
            "django.channels": {
                "handlers": ["stderr"],
                "level": "INFO",
                "propagate": False,
            },
            "daphne.server": {
                "handlers": ["stderr"],
                "level": "INFO",
                "propagate": False,
            },
            "daphne.http_protocol": {
                "handlers": ["stderr"],
                "level": "INFO",
                "propagate": False,
            },
            "daphne.ws_protocol": {
                "handlers": ["stderr"],
                "level": "INFO",
                "propagate": False,
            },
            "django.utils.autoreload": {"level": "ERROR", "propagate": False},
            "apps": {
                "handlers": ["stderr"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {"handlers": ["stderr"], "level": "ERROR", "propagate": False},
    }

    def _update_logging(self, config, level=None, formater=None, handler=None):
        for logger in config["loggers"]:
            if logger in ("django.utils.autoreload"):
                continue
            if handler:
                if not isinstance(handler, list):
                    handler = [handler]
                if "null" not in config["loggers"][logger]["handlers"]:
                    config["loggers"][logger]["handlers"] = handler

            config["loggers"][logger]["level"] = level

        config["root"]["handlers"] = handler
        config["root"]["level"] = level

        for handler in config["handlers"]:
            if handler == "file":
                continue
            if formater:
                config["handlers"][handler]["formatter"] = formater

        return config
