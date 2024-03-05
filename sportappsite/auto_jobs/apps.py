from django.apps import AppConfig


class AutoJobsConfig(AppConfig):
    name = "auto_jobs"

    def ready(self):
        from .signals import fetch_series
        from .signals import score_match
        from .signals import score_series
