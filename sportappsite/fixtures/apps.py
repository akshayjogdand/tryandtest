from django.apps import AppConfig


class FixturesConfig(AppConfig):
    name = "fixtures"

    def ready(self):
        from .signals import signals
