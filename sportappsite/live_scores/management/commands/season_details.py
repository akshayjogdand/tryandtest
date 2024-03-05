import dateutil.parser
import logging

import pycricket

from django.core.management.base import BaseCommand

from fixtures.models import (
    Squad,
    Match,
    Tournament,
    Team,
    PlayerTournamentHistory,
    Player,
)

from live_scores.models import Properties


class Command(BaseCommand):
    logger = logging.getLogger("live_scores.ball_by_ball")

    def add_arguments(self, parser):

        # Positional arguments
        parser.add_argument("season_key", nargs="+", type=str)

    def get_squad(self, team_key, existing_squad, tournament, match):

        create_squad = False

        if team_key:
            if team_key != "tbc":
                team_key_list = Properties.get_obj_cricketapi(team_key)
                if team_key_list:

                    if existing_squad is None:
                        create_squad = True
                    elif existing_squad.team != team_key_list[0].team:
                        create_squad = True

        if create_squad:
            squad = Squad()
            squads = Squad.objects.filter(team=team_key_list[0].team).order_by(
                "-squad_number"
            )
            if not squads:
                squad.squad_number = 100
            else:
                squad.squad_number = squads[0].squad_number + 1
            squad.team = team_key_list[0].team
            squad.tournament = tournament
            squad.save()
            self.logger.info(
                "Created Squad: Team: %s Tournament: %s Match: %s  %s",
                squad.team.name,
                squad.tournament.name,
                match.reference_name,
                match.name,
            )
            return squad

        else:
            return existing_squad

    def handle(self, *args, **options):
        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="eed6178168b033260de5884da95eebb5",
            secret_key="0d1cda0c712d0b861841765a9c5673d4",
            app_id="2208",
            store_handler=handler,
        )

        # Persist information about the tournament
        for season_key in options["season_key"]:

            active_season_info = start.get_season(season_key)
            if active_season_info["status_code"] == 200:
                tournament_key_list = Properties.get_obj_cricketapi(season_key)
                if not tournament_key_list:
                    tournament = Tournament()
                    tournament_list = Tournament.objects.filter(
                        name=active_season_info["data"]["season"]["name"]
                    )
                    if not tournament_list:
                        tournament.name = active_season_info["data"]["season"]["name"]
                        tournament.save()
                        self.logger.info(
                            "Created Tournament: Tournament: %s", tournament.name
                        )
                    else:
                        tournament = tournament_list[0]

                    tournament_key = Properties()
                    tournament_key.tournament = tournament
                    tournament_key.property_value = season_key
                    tournament_key.save()
                    self.logger.info(
                        "Created Tournament Key: Tournament: %s, Tournament_Key: %s",
                        tournament.name,
                        tournament_key.property_value,
                    )
                else:
                    tournament = tournament_key_list[0].tournament

                # Persist information about the team
                if len(active_season_info) > 0 and "data" in active_season_info.keys():
                    team_keys = active_season_info["data"]["season"]["teams"].keys()

                    for team_key in team_keys:

                        active_team_info = start.get_season_team(
                            season_key, team_key, "none"
                        )
                        if active_team_info["status_code"] == 200:
                            team_key_list = Properties.get_obj_cricketapi(team_key)
                            if not team_key_list:
                                team = Team()
                                teams = Team.objects.filter(
                                    name=active_team_info["data"]["name"]
                                )
                                if not teams:
                                    team.name = active_team_info["data"]["name"]
                                    team.save()
                                    self.logger.info(
                                        "Created Team: Team: %s", team.name
                                    )
                                else:
                                    team = teams[0]

                                team_key_obj = Properties()
                                team_key_obj.team = team
                                team_key_obj.tournament = tournament
                                team_key_obj.property_value = team_key
                                team_key_obj.save()
                                self.logger.info(
                                    "Created Team Key: Team: %s, Team_Key: %s",
                                    team.name,
                                    team_key_obj.property_value,
                                )
                            else:
                                team = team_key_list[0].team

                            # Populating players
                            if len(active_team_info["data"]["players"]) > 0:
                                for player_key in active_team_info["data"][
                                    "players"
                                ].keys():

                                    player = Player()
                                    player_key_list = Properties.get_obj_cricketapi(
                                        player_key
                                    )
                                    if not player_key_list:
                                        player_list = Player.objects.filter(
                                            name=active_team_info["data"]["players"][
                                                player_key
                                            ]["name"]
                                        )
                                        if not player_list:
                                            player.name = active_team_info["data"][
                                                "players"
                                            ][player_key]["name"]
                                            player.save()
                                            self.logger.info(
                                                "Created Player: Player: %s",
                                                player.name,
                                            )
                                        else:
                                            player = player_list[0]

                                        player_key_obj = Properties()
                                        player_key_obj.player = player
                                        player_key_obj.property_value = player_key
                                        player_key_obj.save()
                                        self.logger.info(
                                            "Created Player Key: Player: %s, Player_Key: %s",
                                            player.name,
                                            player_key_obj.property_value,
                                        )
                                    else:
                                        player = player_key_list[0].player

                                    try:
                                        pth = PlayerTournamentHistory.objects.get(
                                            player=player,
                                            team=team,
                                            tournament=tournament,
                                        )
                                    except PlayerTournamentHistory.DoesNotExist:
                                        pth = PlayerTournamentHistory()
                                        pth.player = player
                                        pth.team = team
                                        pth.tournament = tournament
                                        pth.status = (
                                            PlayerTournamentHistory.PLAYER_ACTIVE
                                        )
                                        try:
                                            pth.save()
                                        except:
                                            es = (
                                                f"Error saving PlayerTournamentHistory for: "
                                                f"Player={player.name}, Key={player_key}, Team={team}, "
                                                f"Tournament={tournament.name}"
                                            )

                                            self.logger.error(es)
                                            self.logger.error(
                                                "Possibly in multiple teams?"
                                            )

                                        else:
                                            self.logger.info(
                                                "Created Player Tournament History:"
                                                " Player: %s, Tournament: %s, Team: %s",
                                                player.name,
                                                tournament.name,
                                                team.name,
                                            )

                    # else:
                    # call Error function and continue

                    # match details
                    match_keys = active_season_info["data"]["season"]["matches"].keys()
                    count = 1

                    for match_key in match_keys:
                        # print(match_key)
                        match_key_list = Properties.get_obj_cricketapi(match_key)
                        match = Match()
                        match_list = Match.objects.filter(
                            reference_name=active_season_info["data"]["season"][
                                "matches"
                            ][match_key]["related_name"],
                            tournament=tournament,
                        )

                        if not match_key_list:  # if key is not there
                            if match_list:  # if match is there
                                match = match_list[0]
                            else:  # match doesn't exist and create a new one
                                match.match_date = dateutil.parser.parse(
                                    active_season_info["data"]["season"]["matches"][
                                        match_key
                                    ]["start_date"]["iso"]
                                )
                                match.match_number = count
                                count = count + 1
                                match.match_status = Match.SCHEDULED
                                match.tournament = tournament
                                match.match_type = Match.T_TWENTY
                                match.reference_name = active_season_info["data"][
                                    "season"
                                ]["matches"][match_key]["related_name"]
                                match.name = match.reference_name
                                match.save()
                                self.logger.info(
                                    "Created Match: Match: %s, Tournament: %s",
                                    match.reference_name,
                                    tournament.name,
                                )

                            match_key_obj = Properties()
                            match_key_obj.match = match
                            match_key_obj.property_value = match_key
                            match_key_obj.save()
                            self.logger.info(
                                "Created Match Key: Match: %s, Match_Key: %s",
                                match.reference_name,
                                match_key_obj.property_value,
                            )
                        else:
                            match = match_key_list[0].match
                            match.match_date = dateutil.parser.parse(
                                active_season_info["data"]["season"]["matches"][
                                    match_key
                                ]["start_date"]["iso"]
                            )

                        # Getting the Squad Information:
                        if match.toss_winner is None:
                            team_one_key = active_season_info["data"]["season"][
                                "matches"
                            ][match_key]["teams"]["a"]["match"]["season_team_key"]
                            team_two_key = active_season_info["data"]["season"][
                                "matches"
                            ][match_key]["teams"]["b"]["match"]["season_team_key"]
                            match.team_one = self.get_squad(
                                team_one_key, match.team_one, tournament, match
                            )
                            match.team_two = self.get_squad(
                                team_two_key, match.team_two, tournament, match
                            )
                            try:
                                match.save()
                            except:
                                self.logger.error(
                                    "Error in creating match: %s ", match.name
                                )


# else:
# call error function and continue
