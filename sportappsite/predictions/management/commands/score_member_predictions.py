from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Match

from predictions.scoring import score_member_predictions


class Command(BaseCommand):
    help = "Score all Member Predictions for a given Match"

    def add_arguments(self, parser):
        parser.add_argument("--match-id", type=int, required=True, help="Match ID")

    @transaction.atomic
    def handle(self, match_id, *args, **options):
        try:
            match = Match.objects.get(id=match_id)
            score_member_predictions(match)

        except Match.DoesNotExist:
            raise CommandError("Match with ID: {}".format(match_id))

        except Exception as ex:
            raise ex
