from django.apps import AppConfig


class RewardsConfig(AppConfig):
    name = "rewards"

    def ready(self):
        from .signals import enable_group_reward
