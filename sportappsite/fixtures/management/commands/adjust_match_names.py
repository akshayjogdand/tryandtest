from django.core.management.base import BaseCommand

from fixtures.models import Match, Tournament


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)

        for match in Match.objects.filter(tournament=tournament).order_by("match_date"):
            match.assign_name()
            match.assign_short_display_name()
            match.save()
