from django.apps import AppConfig


class Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self):
        from . import receivers  # NOQA isort:skip
