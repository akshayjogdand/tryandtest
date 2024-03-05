from django.db import transaction

from collections import OrderedDict

from fixtures.models import Team, Player, Match, Tournament, PlayerTournamentHistory

from members.models import MemberGroup, LeaderBoardEntry, GroupLeaderBoard

from predictions.models import MemberTournamentPrediction, TouramentPredictionScore


# Teams
# England
team_one = Team.objects.get(id=12)

# New Zealand
team_two = Team.objects.get(id=14)

# India
team_three = Team.objects.get(id=13)

# Australia
team_four = Team.objects.get(id=10)

# Afghanistan
worst_team = Team.objects.get(id=21)


# Batsmen
# Rohit Sharma
batsman_one = Player.objects.get(id=12)

# David Warner
batsman_two = Player.objects.get(id=165)

# Shakib Al Hasan
batsman_three = Player.objects.get(id=65)

# Kane Williamson
batsman_four = Player.objects.get(id=411)

# Joe Root
batsman_five = Player.objects.get(id=291)


# Bowlers
# Mitchell Starc
bowler_one = Player.objects.get(id=116)

# Lockie Ferguson
bowler_two = Player.objects.get(id=239)

# Jofra Archer
bowler_three = Player.objects.get(id=394)

# Mustafizur Rahman
bowler_four = Player.objects.get(id=157)

# Jasprit Bumrah
bowler_five = Player.objects.get(id=368)


# Most Valuable Players
# Rohit Sharma
mvp_one = Player.objects.get(id=12)

# Shakib Al Hasan
mvp_two = Player.objects.get(id=65)

# David Warner
mvp_three = Player.objects.get(id=165)

# Aaron Finch
mvp_four = Player.objects.get(id=1)

# Ben Stokes
mvp_five = Player.objects.get(id=241)

tps_team_vars = ["team_one", "team_two", "team_three", "team_four"]

winning_teams = set([team_one, team_two, team_three, team_four])


def add_teams(tps, teams):
    vars_to_set = tps_team_vars.copy()
    for team in teams:
        v = vars_to_set.pop(0)
        setattr(tps, v, team)


def teams(prediction):
    points = 0

    # picked tournament winner
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick Tournament Winner (+6000)"
    if prediction.tournament_winning_team == team_one:
        points = points + 6000
        tps.points = 6000
        tps.team_one = team_one
        tps.save()

    # picked finalist in order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick Finalist in correct order (+4000)"
    if (
        prediction.tournament_winning_team == team_one
        and prediction.runner_up == team_two
    ):
        points = points + 4000
        tps.points = 4000
        tps.team_one = team_one
        tps.team_two = team_two
        tps.save()

    # picked finalist in any order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick Finalists (+2000)"
    if (
        prediction.tournament_winning_team == team_two
        and prediction.runner_up == team_one
    ):
        points = points + 2000
        tps.points = 2000
        tps.team_one = team_two
        tps.team_two = team_one
        tps.save()

    # picked all 4 teams in order:
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick all 4 Top Teams in ranked order (+4000)"
    if (
        prediction.tournament_winning_team == team_one
        and prediction.runner_up == team_two
        and prediction.top_team_three == team_three
        and prediction.top_team_four == team_four
    ):
        points = points + 4000
        tps.points = 4000
        tps.team_one = team_one
        tps.team_two = team_two
        tps.team_three = team_three
        tps.team_four = team_four
        tps.save()

    predicted_teams = set(prediction.team_vars().values())
    correctly_predicted_teams = predicted_teams.intersection(winning_teams)

    # picked all 4 teams in no order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick all 4 Top Teams in no order (+2000)"
    if len(correctly_predicted_teams) == 4:
        points = points + 2000
        tps.points = 2000
        tps.team_one = prediction.tournament_winning_team
        tps.team_two = prediction.runner_up
        tps.team_three = prediction.top_team_three
        tps.team_four = prediction.top_team_four
        tps.save()

    # picked 3 teams in no order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick 3 from Top 4 Teams in no order (+1500)"
    if len(correctly_predicted_teams) == 3:
        points = points + 1500
        tps.points = 1500
        add_teams(tps, correctly_predicted_teams)
        tps.save()

    # picked 2 teams in no order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick 2 from Top 4 Teams in no order (+1000)"
    if len(correctly_predicted_teams) == 2:
        points = points + 1000
        tps.points = 1000
        add_teams(tps, correctly_predicted_teams)
        tps.save()

    # picked 1 team in no order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Pick 1 from Top 4 Teams in no order (+500)"
    if len(correctly_predicted_teams) == 1:
        points = points + 500
        tps.points = 500
        add_teams(tps, correctly_predicted_teams)
        tps.save()

    # last team
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Worst Performing Team (+1000)"
    if prediction.last_team == worst_team:
        points = points + 1000
        tps.points = 1000
        tps.team_one = worst_team
        tps.save()

    return points


def at_least_one_player_from_predicted_winning_team(players, team, tournament):

    for p in players:
        try:
            PlayerTournamentHistory.objects.get(
                player=p, tournament=tournament, team=team
            )
        except PlayerTournamentHistory.DoesNotExist:
            pass
        else:
            return True

    return False


def batsman(prediction):
    points = 0
    players = prediction.batsman_vars().values()

    # batsman
    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == batsman_one:
            tps.rule = "Pick Top Batsman (+1500)"
            points = points + 1500
            tps.points = 1500
            tps.player = player

        if player == batsman_two or player == batsman_three:
            tps.rule = "Pick 2nd or 3rd ranked Batsman from Top 5 (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == batsman_four or player == batsman_five:
            tps.rule = "Pick 4th or 5th ranked Batsman from Top 5 (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    if not at_least_one_player_from_predicted_winning_team(
        players, prediction.tournament_winning_team, prediction.tournament
    ):
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = (
            "No Batsman chosen from your Predicted Winning Team (- all Batsmen points)"
        )
        tps.points = points * -1
        points = 0
        tps.save()

    return points


def bowler(prediction):
    points = 0
    players = prediction.bowler_vars().values()

    # bowler
    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == bowler_one:
            tps.rule = "Pick Top Bowler (+1500)"
            points = points + 1500
            tps.points = 1500
            tps.player = player

        if player == bowler_two or player == bowler_three:
            tps.rule = "Pick 2nd or 3rd ranked Bowler from Top 5 (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == bowler_four or player == bowler_five:
            tps.rule = "Pick 4th or 5th ranked Bowler from Top 5 (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    if not at_least_one_player_from_predicted_winning_team(
        players, prediction.tournament_winning_team, prediction.tournament
    ):
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = (
            "No Bowler chosen from your Predicted Winning Team (- all Bowler points)"
        )
        tps.points = points * -1
        points = 0
        tps.save()

    return points


def mvp(prediction):
    points = 0
    players = prediction.mvp_vars().values()
    # MVP

    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == mvp_one:
            tps.rule = "Pick Top MVP (+1500)"
            points = points + 1500
            tps.points = 1500
            tps.player = player

        if player == mvp_two or player == mvp_three:
            tps.rule = "Pick 2nd or 3rd ranked MVP (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == mvp_four or player == mvp_five:
            tps.rule = "Pick 4th or 5th ranked MVP (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    if not at_least_one_player_from_predicted_winning_team(
        players, prediction.tournament_winning_team, prediction.tournament
    ):
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = "No MVP chosen from your Predicted Winning Team (- all MVP points)"
        tps.points = points * -1
        points = 0
        tps.save()

    return points


def get_entry(member, entries):
    if entries is None:
        return

    for e in entries:
        if e.member == member:
            return e


def create_tournament_leaderboard(match, board, group, entries):
    previous_match = Match.objects.filter(
        tournament=match.tournament, match_number=match.match_number - 1
    ).first()
    previous_board = GroupLeaderBoard.objects.get(
        match=previous_match, member_group=group
    )
    previous_board_entries = list(previous_board.entries.all())

    le_cache = []
    for le in entries:
        previous_entry = get_entry(le.member, previous_board_entries)
        if previous_entry is not None:
            le.previous_points = previous_entry.total
            le.previous_position = previous_entry.position_now
            le.total = le.tournament_predictions_score + previous_entry.total
        else:
            le.previous_points = 0
            le.previous_position = 0
            le.total = le.tournament_predictions_score + previous_entry.total

        le_cache.append(le)
        le.save()

    le_cache.sort(key=lambda e: e.previous_position)
    le_cache.sort(key=lambda e: e.total, reverse=True)
    for position, le in enumerate(le_cache, 1):
        le.position_now = position
        if le.previous_position != 0:
            le.movement = (le.position_now - le.previous_position) * -1
        else:
            le.movement = le.position_now
        le.save()

    board.save()
    return board


@transaction.atomic
def run(fake_match_id, *args):
    fake_match = Match.objects.get(id=fake_match_id)
    tournament = Tournament.objects.get(id=5)

    # clear old scores
    for tps in TouramentPredictionScore.objects.filter(
        prediction__tournament=tournament
    ).all():
        tps.delete()

    for member_group in MemberGroup.objects.filter(tournaments__in=[tournament]):
        le_cache = []

        try:
            board = GroupLeaderBoard.objects.get(
                member_group=member_group, match=fake_match
            )
            for le in LeaderBoardEntry.objects.filter(leader_board=board):
                le.delete()
            board.delete()
            board = None

        except GroupLeaderBoard.DoesNotExist:
            board = None

        board = GroupLeaderBoard()
        board.member_group = member_group
        board.match = fake_match
        board.board_number = fake_match.match_number
        board.is_tournament_leaderboard = True
        board.save()

        for prediction in MemberTournamentPrediction.objects.filter(
            member_group=member_group, tournament=tournament
        ).all():
            points = 0
            points = points + teams(prediction)
            points = points + batsman(prediction)
            points = points + bowler(prediction)
            points = points + mvp(prediction)

            leaderboard_entry = LeaderBoardEntry()
            leaderboard_entry.leader_board = board
            leaderboard_entry.member = prediction.member
            leaderboard_entry.this_match = 0
            leaderboard_entry.tournament_predictions_score = points
            leaderboard_entry.save()
            le_cache.append(leaderboard_entry)

        create_tournament_leaderboard(fake_match, board, member_group, le_cache)


"""
import datetime
t = Tournament.objects.get(id=5)
m = Match()

m.tournament = t
m.match_number = 49
m.name = 'CWC 2019, Final Scores: pre-Tournament Predictions + Match Predictions'
m.short_display_name = 'CWC 2019, Final Scores'
m.match_date = datetime.datetime.utcnow()
m.match_type = Match.ONE_DAY
m.match_status = Match.COMPLETED
m.save()
m.id

"""
