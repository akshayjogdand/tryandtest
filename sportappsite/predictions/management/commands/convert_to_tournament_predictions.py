import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Tournament

from predictions.models import (
    MemberTournamentPrediction,
    MemberSubmission,
    GroupSubmissionsConfig,
    TouramentPredictionScore,
)

from members.models import Membership

from sportappsite.constants import TournamentFormats

logger = logging.getLogger("predictions_conversions")


def create_blank_prediction(membership, tournament, tournament_format):
    mp = MemberTournamentPrediction()
    mp.member = membership.member
    mp.member_group = membership.member_group
    mp.tournament = tournament
    mp.prediction_format = tournament_format
    mp.save()

    logger.info(
        "Added blank Tourament Prediction for Membership: {} "
        "Match: {}, Prediction ID={}".format(membership, tournament, mp.id)
    )


def convert_submission(submission):
    mp = MemberTournamentPrediction()
    mp.member = submission.member
    mp.member_group = submission.member_group
    mp.tournament = submission.tournament
    mp.prediction_format = submission.submission_format
    mp.save()

    for submitted_item in submission.submission_data.all():
        if hasattr(mp, submitted_item.field_name):
            setattr(mp, submitted_item.field_name, submitted_item.field_value())
        else:

            logger.warning(
                "Unable to convert Tournament submisison ID= field: {}"
                " value: {} to prediction field.".format(
                    submission.id, submitted_item, submitted_item.field_value()
                )
            )
            mp.delete()
            return

    mp.save()
    submission.converted_to_prediction = True
    submission.save()

    logger.info(
        "Converted Tourament Submission ID={} to Prediction ID={}".format(
            submission.id, mp.id
        )
    )


class Command(BaseCommand):
    help = "Turn all Member Tournament Submissions into Tourament Predictions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

        parser.add_argument(
            "--tournament-format",
            required=True,
            type=int,
            help="Tournament Formats: \n {}".format(
                TournamentFormats.type_choices_str()
            ),
        )

    @transaction.atomic
    def handle(self, tournament_id, tournament_format, **options):
        try:
            tournament = Tournament.objects.get(id=tournament_id)

        except Tournament.DoesNotExist:
            raise CommandError(
                "Tournament with id: {} does not exist".format(tournament_id)
            )

        for member_group in tournament.participating_member_groups.all():
            for membership in Membership.objects.filter(member_group=member_group):

                predictions = MemberTournamentPrediction.objects.filter(
                    member=membership.member,
                    member_group=membership.member_group,
                    tournament=tournament,
                    prediction_format=tournament_format,
                )

                for p in predictions:
                    logger.info("Deleting: {}".format(p))
                    TouramentPredictionScore.objects.filter(prediction=p).delete()
                    p.delete()

        logger.info("Beginning conversion for tournament: {}".format(tournament))

        for member_group in tournament.participating_member_groups.all():
            for membership in Membership.objects.filter(
                member_group=member_group, active=True
            ):

                submissions = MemberSubmission.objects.filter(
                    member=membership.member,
                    member_group=membership.member_group,
                    tournament=tournament,
                    submission_format=tournament_format,
                    submission_type=(GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION),
                    is_valid=True,
                ).order_by("-id")

                if submissions.exists():
                    member_submission = submissions.first()
                    convert_submission(member_submission)
                else:
                    create_blank_prediction(membership, tournament, tournament_format)

        logger.info("Finished conversion for tournament: {}".format(tournament))


def convert(tournament_id, tournament_format):
    c = Command()
    c.handle(tournament_id, tournament_format)
