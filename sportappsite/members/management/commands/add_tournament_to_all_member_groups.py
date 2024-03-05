from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import MemberGroup

from fixtures.models import Tournament


class Command(BaseCommand):
    help = "Add a Tournament to all Member Groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        t = Tournament.objects.get(id=tournament_id)

        # A timing/sequence/workflow issue can cause un-intended effetc here.
        # If the goal is to get a Tournament to all Member Group, we need to
        # Remove -> Save -> Add -> Save.
        # This sequence will cause a sync of all the Configs and Rules.
        for mg in MemberGroup.objects.all():
            mg.tournaments.remove(t)
            mg.save()

        for mg in MemberGroup.objects.all():
            mg.tournaments.add(t)
            mg.save()
