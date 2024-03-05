from django.core.management.base import BaseCommand, CommandError

from predictions.models import MatchPrediction, ScoringMethod
from predictions.scoring import score_prediction


class Command(BaseCommand):
    help = (
        "Score a set of Match Predictions against performances, using a chosen method "
    )

    def add_arguments(self, parser):
        parser.add_argument("pid", type=int, help="Prediction ID to score")
        parser.add_argument("sid", type=int, help="Scoring Method ID to use")

    def handle(self, pid, sid, **options):
        try:
            pred = MatchPrediction.objects.get(pk=pid)
            method = ScoringMethod.objects.get(pk=sid)

        except MatchPrediction.DoesNotExist:
            raise CommandError("Prediction with id: {} does not exist".format(pid))
        except ScoringMethod.DoesNotExist:
            raise CommandError("Scoring Method with id: {} does not exist".format(sid))

        total = 0
        for rr in score_prediction(pred, method):
            self.stdout.write(
                "{}, rule: {}, inputs: {}, result: {}".format(
                    rr.player, rr.rule, rr.input_values, rr.result
                )
            )
            total = total + rr.result

        self.stdout.write("\nTotal score is: {}".format(total))
