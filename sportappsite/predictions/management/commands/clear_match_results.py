from django.core.management.base import BaseCommand, CommandError

from fixtures.models import Match
from predictions.models import MatchPrediction, RuleResult


class Command(BaseCommand):
    help = "Clear all Predictions registered against a Match"

    def add_arguments(self, parser):
        parser.add_argument("mid", type=int, help="Match ID")

    def handle(self, mid, **options):
        try:
            match = Match.objects.get(pk=mid)

        except Match.DoesNotExist:
            raise (CommandError("Match with id: {} does not exist").format(mid))

        predictions = MatchPrediction.objects.all().filter(match=match)
        for pred in predictions:
            pred.results.clear()
            pred.scored = False
            pred.total = 0
            pred.super_player_score = 0
            pred.player_one_score = 0
            pred.player_two_score = 0
            pred.save()

        results = RuleResult.objects.all().filter(match=match)
        for r in results:
            r.delete()

        self.stdout.write("Prediction results for Match {} cleared".format(match))
