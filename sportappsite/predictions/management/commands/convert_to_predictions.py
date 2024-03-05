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


def convert_submission(submission):
    mp = MemberPrediction()
    mp.member = submission.member
    mp.member_group = submission.member_group
    mp.match = submission.match
    mp.save()

    for submitted_item in submission.submission_data.all():
        if hasattr(mp, submitted_item.field_name):
            setattr(mp, submitted_item.field_name, submitted_item.field_value())
        else:
            logger.warning(
                "Unable to convert submisison ID= field: {}"
                " value: {} to prediction field.".format(
                    submission.id, submitted_item, submitted_item.value()
                )
            )
            mp.delete()
            return

    mp.save()
    submission.converted_to_prediction = True
    submission.save()

    logger.info(
        "Converted Submission ID={} to Prediction ID={}".format(submission.id, mp.id)
    )


class Command(BaseCommand):
    help = "Turn all Member Submissions into Match Predictions"

    def add_arguments(self, parser):
        parser.add_argument("--match-id", required=True, type=int, help="Match ID")

        parser.add_argument(
            "--delete",
            required=False,
            action="store_true",
            help="Delete existing Predictions.",
        )

    def delete(self, match):
        for member_group in match.tournament.participating_member_groups.all():
            for membership in Membership.objects.filter(member_group=member_group):

                predictions = MemberPrediction.objects.filter(
                    member=membership.member,
                    member_group=membership.member_group,
                    match=match,
                )

                for p in predictions:
                    logger.info("Deleting: {}".format(p))
                    p.delete()

    @transaction.atomic
    def handle(self, match_id, delete, **options):
        try:
            match = Match.objects.get(id=match_id)

        except Match.DoesNotExist:
            raise CommandError("Match with id: {} does not exist".format(match_id))

        if delete:
            self.delete(match)
            return

        logger.info("Beginning conversion for match: {}".format(match))

        for member_group in match.tournament.participating_member_groups.all():
            for membership in Membership.objects.filter(
                member_group=member_group, active=True
            ):

                submissions = MemberSubmission.objects.filter(
                    member=membership.member,
                    member_group=membership.member_group,
                    match=match,
                    submission_type=(GroupSubmissionsConfig.MATCH_DATA_SUBMISSION),
                    is_valid=True,
                ).order_by("-id")

                if submissions.exists():
                    member_submission = submissions.first()
                    convert_submission(member_submission)
                else:
                    create_blank_prediction(membership, match)

        logger.info("Finished conversion for match: {}".format(match))


def convert_submissions_for_match(match_id):
    c = Command()
    c.handle(match_id, False)
