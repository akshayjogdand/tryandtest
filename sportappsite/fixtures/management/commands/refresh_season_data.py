from datetime import timedelta

from django.core.management.base import BaseCommand

from django.utils import timezone

from live_scores.models import Properties

from .schedules import season_details_schedule, fix_match_data_schedule

from ...models import Tournament


class Command(BaseCommand):
    help = "Refresh Season Data for active Touraments -- call once a day."
    "All time calculations are UTC."

    def handle(self, *args, **options):
        today = timezone.now()

        for tournament in Tournament.objects.filter(is_active=True):
            season_key = Properties.objects.get(
                tournament=tournament, match=None, player=None, squad=None, team=None,
            ).property_value

            season_details_time = today
            fix_match_data_time = season_details_time + timedelta(minutes=5)
            season_details_schedule(season_key, season_details_time)
            fix_match_data_schedule(tournament.id, fix_match_data_time)

            print("Fetched latest data and fixed names, etc for: {}".format(tournament))
