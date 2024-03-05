from sportappsite.constants import TournamentFormats

from django.core.management.base import BaseCommand

from ...models import MemberSubmission

from ...stats import update_tournament_submission_stats, tournament_stats_count


class Command(BaseCommand):
    help = "Compute Submissions Stats for Tournament Submissions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

        parser.add_argument(
            "--tournament-format",
            required=True,
            type=int,
            help="Tournament Formats: {}".format(TournamentFormats.type_choices_str()),
        )

        parser.add_argument(
            "--group-id", required=False, type=int, help="Member Group ID"
        )

    def handle(self, tournament_id, tournament_format, group_id, **options):
        select = {
            "submission_type": MemberSubmission.TOURNAMENT_DATA_SUBMISSION,
            "is_valid": True,
            "tournament": tournament_id,
            "member_group__reserved": False,
        }

        if group_id:
            select["member_group"] = group_id

        for ms in (
            MemberSubmission.objects.filter(**select).order_by("submission_time").all()
        ):
            update_tournament_submission_stats(ms.id)

        tournament_stats_count(tournament_id, tournament_format)
