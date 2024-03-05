from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Tournament

from predictions.models import ControlledGroupSubmissionsConfig

from predictions.utils import clone_controlled_config


class Command(BaseCommand):
    help = "Copy all fields in one Controlled Group Config to another for a different Tournament."

    def add_arguments(self, parser):
        parser.add_argument("--from-id", required=True, type=int, help="From CG ID.")

        parser.add_argument(
            "--tournament-id",
            required=True,
            type=int,
            help="Tournament for which config is to be cloned.",
        )

    @transaction.atomic
    def handle(self, from_id, tournament_id, **opts):
        try:
            controlled_config = ControlledGroupSubmissionsConfig.objects.get(id=from_id)
            t = Tournament.objects.get(id=tournament_id)

        except ControlledGroupSubmissionsConfig.DoesNotExist:
            raise CommandError(
                "Control Groupt with id: {} does not exist".format(from_id)
            )

        clone_controlled_config(t, controlled_config)
