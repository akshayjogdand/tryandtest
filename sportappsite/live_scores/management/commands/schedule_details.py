import pycricket

from django.core.management.base import BaseCommand

from fixtures.models import Tournament, Team, Squad, Player

from live_scores.models import Properties


class Command(BaseCommand):
    def handle(self, *args, **options):
        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="eed6178168b033260de5884da95eebb5",
            secret_key="0d1cda0c712d0b861841765a9c5673d4",
            app_id="2208",
            store_handler=handler,
        )
        # file_handler = open("Season_Match_Info", "w+")
        i = 0
        season_info = start.get_recent_seasons()
        while i < len(season_info["data"]):
            season_key = season_info["data"][i]["key"]
            # file_handler.write("Season Key -- "+season_key+"\n")
            active_season_info = start.get_season(season_key)
            if active_season_info["status_code"] == 200:
                tournament = Tournament()
                tournament.name = active_season_info["data"]["season"]["name"]
                tournament.save()
                tournament_key = Properties()
                tournament_key.tournament = tournament
                tournament_key.property_name = "KEYS"
                tournament_key.property_context = "CricketAPI"
                tournament_key.property_value = season_key
                tournament_key.save()
                # Need to handle an error message wherein you
                # have the active_season_info has data but no teams
                if len(active_season_info) > 0 and "data" in active_season_info.keys():
                    team_keys = active_season_info["data"]["season"]["teams"].keys()
                    # Get team_keys from the system.
                    for team_key in team_keys:
                        active_team_info = start.get_season_team(
                            season_key, team_key, "none"
                        )
                        teams = Team.objects.filter(
                            name=active_team_info["data"]["name"]
                        )
                        if not teams:
                            team = Team()
                            team.name = active_team_info["data"]["name"]
                            team.save()
                        else:
                            team = teams[0]
                        team_key_list = Properties.objects.filter(
                            property_value=team_key
                        )
                        if not team_key_list:
                            team_key_obj = Properties()
                            team_key_obj.team = team
                            team_key_obj.property_name = "KEYS"
                            team_key_obj.property_context = "CricketAPI"
                            team_key_obj.property_value = team_key
                            team_key_obj.save()
                        if len(active_team_info["data"]["players"]) > 0:
                            squad = Squad()
                            squad.team = team
                            squad.tournament = tournament
                            squad.squad_number = 100
                            squad.matches_played = "Not Played"
                            squad.save()
                            players = []
                            for player_key in active_team_info["data"][
                                "players"
                            ].keys():
                                # Get Player Details:
                                # player_info =  active_team_info["data"]["players"][player_key]

                                # file_handler.write(
                                # '\t\n'.join('{}{}'.format(key, val) for key,
                                # val in
                                # active_team_info["data"]["players"][player_key].items()))
                                player_list = Player.objects.filter(
                                    name=active_team_info["data"]["players"][
                                        player_key
                                    ]["name"]
                                )
                                if not player_list:
                                    player = Player()
                                    player.name = active_team_info["data"]["players"][
                                        player_key
                                    ]["name"]
                                    player.save()
                                else:
                                    player = player_list[0]
                                player_key_list = Properties.objects.filter(
                                    property_value=player_key
                                )
                                if not player_key_list:
                                    player_key_obj = Properties()
                                    player_key_obj.player = player
                                    player_key_obj.property_name = "KEYS"
                                    player_key_obj.property_context = "CricketAPI"
                                    player_key_obj.property_value = player_key
                                    player_key_obj.save()
                                players.append(player)
                            squad.players = players
                            squad.save()
            i = i + 1


# file_handler.close()

from django.core.management.base import BaseCommand, CommandError
from fixtures.models import *
from live_scores.models import Properties


# Obtaining the handler
class Command(BaseCommand):
    def handle(self, *args, **options):
        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="5936156e626d2dd54e094e1489905b9f",
            secret_key="4feb4994308d1451fd6542d35e1cab11",
            app_id="2208",
            store_handler=handler,
        )
        # file_handler = open("Season_Match_Info", "w+")
        i = 0
        season_info = start.get_recent_seasons()
        while i < len(season_info["data"]):
            season_key = season_info["data"][i]["key"]
            # file_handler.write("Season Key -- "+season_key+"\n")
            active_season_info = start.get_season(season_key)
            if active_season_info["status_code"] == 200:
                tournament = Tournament()
                tournament.name = active_season_info["data"]["season"]["name"]
                tournament.save()
                tournament_key = Properties()
                tournament_key.tournament = tournament
                tournament_key.property_name = "KEYS"
                tournament_key.property_context = "CricketAPI"
                tournament_key.property_value = season_key
                tournament_key.save()
                ## Need to handle an error message wherein you have the active_season_info has data but no teams
                if len(active_season_info) > 0 and "data" in active_season_info.keys():
                    team_keys = active_season_info["data"]["season"]["teams"].keys()
                    # Get team_keys from the system.
                    for team_key in team_keys:
                        active_team_info = start.get_season_team(
                            season_key, team_key, "none"
                        )
                        teams = Team.objects.filter(
                            name=active_team_info["data"]["name"]
                        )
                        if not teams:
                            team = Team()
                            team.name = active_team_info["data"]["name"]
                            team.save()
                        else:
                            team = teams[0]
                        team_key_list = Properties.objects.filter(
                            property_value=team_key
                        )
                        if not team_key_list:
                            team_key_obj = Properties()
                            team_key_obj.team = team
                            team_key_obj.property_name = "KEYS"
                            team_key_obj.property_context = "CricketAPI"
                            team_key_obj.property_value = team_key
                            team_key_obj.save()
                        if len(active_team_info["data"]["players"]) > 0:
                            squad = Squad()
                            squad.team = team
                            squad.tournament = tournament
                            squad.squad_number = 100
                            squad.matches_played = "Not Played"
                            squad.save()
                            players = []
                            for player_key in active_team_info["data"][
                                "players"
                            ].keys():
                                # Get Player Details:
                                # player_info = active_team_info["data"]["players"][player_key]
                                # file_handler.write('\t\n'.join('{}{}'.format(key, val) for key, val in active_team_info["data"]["players"][player_key].items()))
                                player_list = Player.objects.filter(
                                    name=active_team_info["data"]["players"][
                                        player_key
                                    ]["name"]
                                )
                                if not player_list:
                                    player = Player()
                                    player.name = active_team_info["data"]["players"][
                                        player_key
                                    ]["name"]
                                    player.save()
                                else:
                                    player = player_list[0]
                                player_key_list = Properties.objects.filter(
                                    property_value=player_key
                                )
                                if not player_key_list:
                                    player_key_obj = Properties()
                                    player_key_obj.player = player
                                    player_key_obj.property_name = "KEYS"
                                    player_key_obj.property_context = "CricketAPI"
                                    player_key_obj.property_value = player_key
                                    player_key_obj.save()
                                players.append(player)
                            squad.players = players
                            squad.save()
            i = i + 1
        # file_handler.close()
