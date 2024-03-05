from django.apps import AppConfig


class PredictionsConfig(AppConfig):
    name = "predictions"

    def ready(self):
        from .signals.lodge_tournament_closure_jobs import lodge_convert_predictions_job
