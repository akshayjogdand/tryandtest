from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "members"

    def ready(self):
        from .signals import signals
