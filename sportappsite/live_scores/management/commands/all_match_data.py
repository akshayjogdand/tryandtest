import time

from django.core.management.base import BaseCommand

from django.db import transaction

from fixtures.models import Match, Tournament

from .match_details import Command as MDCommand

from .ball_by_ball import Command as BBCommand

from .match_completion import Command as MCCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument("--match-id", type=int, help="Match ID")
        g.add_argument("--tournament-id", type=int, help="Tournament ID")
        parser.add_argument("--match-range", type=str, help="Range of Matches: n-m")

    def handle(self, match_id, tournament_id, match_range, **kwargs):
        if tournament_id:
            t = Tournament.objects.get(id=tournament_id)
            matches = Match.objects.filter(tournament=t).order_by("match_date")

            if match_range:
                start, finish = match_range.split("-")
                matches = Match.objects.filter(
                    tournament=t, match_number__gte=start, match_number__lte=finish
                ).order_by("match_date")
        elif match_id:
            matches = [Match.objects.get(id=match_id)]

        for m in matches:
            time.sleep(5)
            with transaction.atomic():
                match_key = m.properties_set.first().property_value
                print("Fetching data for: {}, key: {}".format(m.name, match_key))

                mdc = MDCommand()
                mdc.handle(match_key)

                bbc = BBCommand()
                bbc.handle(
                    match_key=[match_key],
                    over_interval=2,
                    start_over=1,
                    end_over=20,
                    redo=True,
                    team=None,
                    innings=1,
                )

                mcc = MCCommand()
                mcc.handle(match_key=[match_key])

                print("Done, sleping for 5")
