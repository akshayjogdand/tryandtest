from django.apps import AppConfig


class ConfigurationsConfig(AppConfig):
    name = "configurations"

    def ready(self):
        from .signals import signals
