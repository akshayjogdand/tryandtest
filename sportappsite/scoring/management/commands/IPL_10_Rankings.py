from fixtures.models import Player, Team


def get_team(team_id):
    if team_id == "" or team_id is None:
        return None
    else:
        return Team.objects.get(id=team_id)


def get_player(name):
    if name == "" or name is None:
        return None
    else:
        try:
            return Player.objects.filter(name=name)[0]
        except Exception as exp:
            print("Error fetching Player: {}".format(name))
            raise exp


BATSMAN_RANKING = {
    1: get_player("David Warner"),
    2: get_player("Gautam Gambhir"),
    3: get_player("Shikhar Dhawan"),
    4: get_player("Steve Smith"),
    5: get_player("Suresh Raina"),
    6: get_player("Hashim Amla"),
    7: get_player("Manish Pandey"),
    8: get_player("Parthiv Patel"),
    9: get_player("Rahul Tripathi"),
    10: get_player("Robin Uthappa"),
}


BOWLER_RANKING = {
    1: get_player("Bhuvneshwar Kumar"),
    2: get_player("Jaydev Unadkat"),
    3: get_player("Jasprit Bumrah"),
    4: get_player("Mitchell McClenaghan"),
    5: get_player("Imran Tahir"),
    6: get_player("Rashid Khan"),
    7: get_player("Chris Woakes"),
    8: get_player("Sandeep Sharma"),
    9: get_player("Umesh Yadav"),
    10: get_player("Pawan Negi"),
}

TEAM_RANKING = {
    1: get_team(1),
    2: get_team(9),
    3: get_team(4),
    4: get_team(8),
    5: get_team(5),
    6: get_team(3),
    7: get_team(2),
    8: get_team(6),
}
