from datetime import timedelta

from django.core.management.base import BaseCommand

from django.utils import timezone

from live_scores.models import Properties

from .schedules import *


class Command(BaseCommand):
    help = "Register various schedules for today's matches."
    "All time calculations are UTC."

    def handle(self, *args, **options):
        today = timezone.now()

        for match in Match.objects.filter(
            match_date__date=today, tournament__is_active=True
        ):
            season_key = Properties.objects.get(
                tournament=match.tournament,
                match=None,
                player=None,
                squad=None,
                team=None,
            ).property_value

            try:

                match_key = Properties.objects.get(
                    tournament=None, match=match, player=None, squad=None, team=None
                ).property_value
            except Properties.MultipleObjectsReturned:
                print(f"Multiple property keys returned for Match: {match}")
                print(f"Will now use key with highest ID")

                match_key = (
                    Properties.objects.filter(
                        tournament=None, match=match, player=None, squad=None, team=None
                    )
                    .latest("id")
                    .property_value
                )

                print(f"Using key: {match_key}")

            submission_lock_time = match.match_date - timedelta(minutes=30)
            post_toss_changes_lock_time = match.match_date

            # lock_match_submisisons_schedule(match.id, submission_lock_time)
            poll_match_details_schedule(match_key, match.id, submission_lock_time)
            lock_match_post_toss_changes_schedule(match.id, post_toss_changes_lock_time)

            print("Match: {}, ID: {}".format(match, match.id))
            print("\tLocking Submissions: {}".format(submission_lock_time))
            print("\tUn-locking Post Toss changes: {}".format(submission_lock_time))
            print(
                "\tStart polling Match Playing XI details for match key {}"
                " at: {}".format(match_key, submission_lock_time)
            )
            print("\tLocking Post Toss Changes: {}".format(post_toss_changes_lock_time))

            if match.match_type == Match.ONE_DAY:
                season_details_time = post_toss_changes_lock_time + timedelta(hours=10)
                is_test_match = False

            elif match.match_type == Match.T_TWENTY:
                season_details_time = post_toss_changes_lock_time + timedelta(
                    hours=4, minutes=30
                )
                is_test_match = False

            else:
                season_details_time = post_toss_changes_lock_time + timedelta(hours=105)
                is_test_match = True

            fix_match_data_time = season_details_time + timedelta(minutes=5)
            match_details_time = season_details_time + timedelta(minutes=5)
            fetch_scores_time = match_details_time + timedelta(minutes=5)
            match_completion_time = fetch_scores_time + timedelta(minutes=30)
            player_scoring_time = match_completion_time + timedelta(minutes=5)
            member_scoring_time = player_scoring_time + timedelta(minutes=5)
            player_stats_time = member_scoring_time + timedelta(minutes=5)

            season_details_schedule(season_key, season_details_time)
            poll_match_details_once_schedule(match_key, match.id, match_details_time)
            fetch_scores_schedule(match_key, fetch_scores_time, is_test_match)
            match_completion_schedule(match_key, match_completion_time)
            match_scoring_schedule(match.id, player_scoring_time)
            member_scoring_schedule(match.id, member_scoring_time)
            player_stats_schedule(match.id, player_stats_time)
            fix_match_data_schedule(match.tournament.id, fix_match_data_time)

            print("\n\t\tAUTO SCORING")
            print("\tSeason Details: {}".format(season_details_time))
            print("\tFix Match Data: {}".format(fix_match_data_time))
            print("\tMatch Details: {}".format(match_details_time))
            print("\tFetch Scores: {}".format(fetch_scores_time))
            print("\tMatch Completion: {}".format(match_completion_time))
            print("\tPlayer Scoring: {}".format(player_scoring_time))
            print("\tMember Scoring: {}".format(member_scoring_time))
            print("\tPlayer Stats: {}".format(player_stats_time))
            print("\n\n")
