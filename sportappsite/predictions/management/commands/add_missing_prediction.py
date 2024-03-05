import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Match

from predictions.models import (
    MemberPrediction,
    MemberSubmission,
    GroupSubmissionsConfig,
)

from members.models import Membership

logger = logging.getLogger("predictions_conversions")


def create_blank_prediction(membership, match):
    mp = MemberPrediction()
    mp.member = membership.member
    mp.member_group = membership.member_group
    mp.match = match
    mp.save()

    logger.info(
        "Addded blank Prediction for Membership: {} "
        "Match: {}, Prediction ID={}".format(membership, match, mp.id)
    )


class Command(BaseCommand):
    help = "Add blank Member Predictions for a Match"

    def add_arguments(self, parser):
        parser.add_argument("--match-id", required=True, type=int, help="Match ID")

    @transaction.atomic
    def handle(self, match_id, **options):
        try:
            match = Match.objects.get(id=match_id)

        except Match.DoesNotExist:
            raise CommandError("Match with id: {} does not exist".format(match_id))

        for member_group in match.tournament.participating_member_groups.all():
            for membership in Membership.objects.filter(member_group=member_group):

                submissions = MemberSubmission.objects.filter(
                    member=membership.member,
                    member_group=membership.member_group,
                    match=match,
                    submission_type=(GroupSubmissionsConfig.MATCH_DATA_SUBMISSION),
                    is_valid=True,
                ).order_by("-id")

                if not submissions.exists():
                    create_blank_prediction(membership, match)
