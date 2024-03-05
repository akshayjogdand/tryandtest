from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import MemberGroup

from members.utils import get_or_create_group_rules_from_defaults

from predictions.utils import create_or_update_submission_config_for_tournament

from fixtures.models import Tournament


class Command(BaseCommand):
    help = (
        "Ensure all Member Groups have updated copy of Tournament rules "
        + "and submission configs"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        t = Tournament.objects.get(id=tournament_id)
        for mg in MemberGroup.objects.filter(tournaments__in=[t]):
            create_or_update_submission_config_for_tournament(mg, t)
            get_or_create_group_rules_from_defaults(mg, t)
