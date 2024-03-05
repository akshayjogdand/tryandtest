import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Match

from predictions.models import MemberPrediction, MemberSubmission

logger = logging.getLogger("predictions_conversions")


class Command(BaseCommand):
    help = "Turn all Member Submissions into Match Predictions"

    def add_arguments(self, parser):
        parser.add_argument("--match-id", required=True, type=int, help="Match ID")

    @transaction.atomic
    def handle(self, match_id, **options):
        try:
            match = Match.objects.get(id=match_id)

        except Match.DoesNotExist:
            raise CommandError("Match with id: {} does not exist".format(match_id))

        logger.info("Reverting Prediction conversion for match: {}".format(match))

        for m in MemberSubmission.objects.filter(
            match=match, submission_type=MemberSubmission.MATCH_DATA_SUBMISSION
        ):
            if m.converted_to_prediction:
                m.converted_to_prediction = False
                m.save()

        for p in MemberPrediction.objects.filter(match=match):
            p.delete()

        logger.info("Finished revert Prediction conversion for match: {}".format(match))
