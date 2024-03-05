import pycricket
from fixtures.models import *


# Obtaining the handler
handler = pycricket.RcaStorageHandler()
start = pycricket.RcaApp(
    access_key="4ddd528312aa7b436f156c1f876b8ee3",
    secret_key="72431033a19d0bfd47156cda503309c2",
    app_id="2208",
    store_handler=handler,
)

file_handler = open("Season_Match_Info", "w+")
i = 0
season_info = start.get_recent_seasons()
while i < len(season_info["data"]):
    season_key = season_info["data"][i]["key"]
    file_handler.write("Season Key -- " + season_key + "\n")
    active_season_info = start.get_season(season_key)
    ## Need to handle an error message wherein you have the active_season_info has data but no teams
    ## This happens for irepak_2018
    if len(active_season_info) > 0 and "data" in active_season_info.keys():
        team_keys = active_season_info["data"]["season"]["teams"].keys()
        for team_key in team_keys:
            file_handler.write("\t Team Key -- " + team_key + "\n")
            # if "2017" not in season_key:
            active_team_info = start.get_season_team(season_key, team_key, "none")
            if len(active_team_info["data"]["players"]) > 0:
                file_handler.write("\t Players:\n")
                for player_key in active_team_info["data"]["players"].keys():
                    # Get Player Details:
                    # player_info = active_team_info["data"]["players"][player_key]
                    file_handler.write(
                        "\t\n".join(
                            "{}{}".format(key, val)
                            for key, val in active_team_info["data"]["players"][
                                player_key
                            ].items()
                        )
                    )
    i = i + 1
file_handler.close()
