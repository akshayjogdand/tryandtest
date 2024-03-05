from django.apps import AppConfig


class StatsConfig(AppConfig):
    name = "stats"

    def ready(self):
        super(StatsConfig, self).ready()
        from stats.signals import process_import_file
        from stats.signals import live_scoring
