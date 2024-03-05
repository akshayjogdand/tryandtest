import datetime

import pycricket

import logging

from django.utils import timezone

from django.core.management.base import BaseCommand

from fixtures.models import Match, Player, Squad

from live_scores.models import Properties

from stats.models import MatchPerformance


class Command(BaseCommand):

    logger = logging.getLogger("live_scores.ball_by_ball")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("match_key", type=str)

    def handle(self, match_key, *args, **options):
        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="eed6178168b033260de5884da95eebb5",
            secret_key="0d1cda0c712d0b861841765a9c5673d4",
            app_id="2208",
            store_handler=handler,
        )

        # Get Match Object
        active_match_info = start.get_match(match_key)
        match_keys = Properties.get_obj_cricketapi(match_key)
        if match_keys:
            match = match_keys[0].match
            match.match_status = Match.LIVE

            # Toss Info
            # Set toss_winner
            if active_match_info["data"]["card"]["toss"]:
                if active_match_info["data"]["card"]["toss"]["won"] == "a":
                    match.toss_winner = match.team_one
                if active_match_info["data"]["card"]["toss"]["won"] == "b":
                    match.toss_winner = match.team_two

                # Set toss_decision
                if active_match_info["data"]["card"]["toss"]["decision"] == "bowl":
                    match.toss_decision = Match.BOWL
                if active_match_info["data"]["card"]["toss"]["decision"] == "bat":
                    match.toss_decision = Match.BAT

                # Set toss_time and match_start_time
                match.toss_time = timezone.now()
                match.match_start_time = timezone.now() + datetime.timedelta(minutes=30)

                self.logger.info("Updated Toss Information")

            # Get Squad information
            teams = active_match_info["data"]["card"]["teams"]

            for team_ref in teams:

                squad = Squad()

                if team_ref == "a":
                    squad = match.team_one
                if team_ref == "b":
                    squad = match.team_two

                if active_match_info["data"]["card"]["teams"][team_ref]["match"][
                    "playing_xi"
                ]:
                    playing_xi = active_match_info["data"]["card"]["teams"][team_ref][
                        "match"
                    ]["playing_xi"]
                    for player_key in playing_xi:
                        player = Player()
                        player_keys = Properties.get_obj_cricketapi(player_key)
                        if player_keys:
                            player = player_keys[0].player

                        else:

                            player_stats = start.get_player_stats(player_key, "ipl")
                            if player_stats["status_code"] == 200:
                                player_list = Player.objects.filter(
                                    name=player_stats["data"]["player"]["name"]
                                )
                                # This Condition should not come
                                if not player_list:
                                    player.name = player_stats["data"]["player"]["name"]
                                    player.save()
                                    self.logger.info(
                                        "Created Player: Player: %s", player.name
                                    )
                                else:
                                    player = player_list[0]

                            else:
                                # call the Error function and continue
                                player.name = player_key
                                self.logger.info(
                                    "Created Player: Player: %s", player.name
                                )
                                player.save()

                            player_key_obj = Properties()
                            player_key_obj.player = player
                            player_key_obj.property_value = player_key
                            player_key_obj.save()
                            self.logger.info(
                                "Created Player Key: Player: %s, Player_Key: %s",
                                player.name,
                                player_key_obj.property_value,
                            )

                        squad.players.add(player)
                        self.logger.info(
                            "Added Player to Playing XI: Player: %s, Team: %s",
                            player.name,
                            squad.team.name,
                        )

            match.save()


# else:
# call error function and exit
