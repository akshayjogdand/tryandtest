from django.core.management.base import BaseCommand

from fixtures.models import Match, Tournament

from django.db import transaction


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)

        for match in Match.objects.filter(tournament=tournament):
            if "Test Match" in match.reference_name:
                match.match_type = Match.TEST
                match.save()
            elif "ODI Match" in match.reference_name:
                match.match_type = Match.ONE_DAY
                match.save()

        for f in (Match.ONE_DAY, Match.TEST, Match.T_TWENTY):
            for i, match in enumerate(
                Match.objects.filter(tournament=tournament, match_type=f).order_by(
                    "match_date"
                ),
                1,
            ):
                match.match_number = i
                match.assign_name()
                match.assign_short_display_name()
                match.save()
