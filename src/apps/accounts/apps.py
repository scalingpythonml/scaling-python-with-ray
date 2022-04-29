from django.apps import AppConfig


class Config(AppConfig):
    name = "apps.accounts"

    def ready(self):
        from . import receivers  # NOQA isort:skip
