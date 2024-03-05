from django.core.management.base import BaseCommand

from fixtures.models import Match, Tournament


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)

        for i, match in enumerate(
            Match.objects.filter(tournament=tournament).order_by("match_date"), 1
        ):
            match.match_number = i
            match.save()
