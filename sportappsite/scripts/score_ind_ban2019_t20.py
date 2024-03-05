from django.db import transaction

from fixtures.models import Team, Player, Match, Tournament, PlayerTournamentHistory

from members.models import MemberGroup, LeaderBoardEntry, GroupLeaderBoard

from predictions.models import MemberTournamentPrediction, TouramentPredictionScore


# Teams
# India
team_one = Team.objects.get(id=13)

# Batsmen
# Naim
batsman_one = Player.objects.get(id=557)

# Shreyas Iyer
batsman_two = Player.objects.get(id=32)

# Bowlers
# Deepak Chahar
bowler_one = (Player.objects.get(id=127),)

# Yuzvendra Chahal, Aminul Islam, Shaiful Islam
bowler_two = (
    Player.objects.get(id=402),
    Player.objects.get(id=555),
    Player.objects.get(id=280),
)

# Most Valuable Players
# Chahar
mvp_one = Player.objects.get(id=127)

# Rohit sharma
mvp_two = Player.objects.get(id=12)

tps_team_vars = ["team_one"]

winning_teams = set([team_one])

win_series_margin = 1


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
    tps.rule = "Pick Tournament Winner (+1000)"
    if prediction.tournament_winning_team == team_one:
        points = points + 1000
        tps.points = 1000
        tps.team_one = team_one
        tps.save()

    return points


def batsman(prediction):
    points = 0
    players = prediction.batsman_vars().values()

    # batsman
    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == batsman_one:
            tps.rule = "Pick Top Run Scorer (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == batsman_two:
            tps.rule = "Pick 2nd best Run Scorer (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def bowler(prediction):
    points = 0
    players = prediction.bowler_vars().values()

    # bowler
    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player in bowler_one:
            tps.rule = "Pick Player with most Wickets (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player in bowler_two:
            tps.rule = "Pick Player with 2nd highest Wickets (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
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
            tps.rule = "Pick Top MVP (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == mvp_two:
            tps.rule = "Pick 2nd ranked MVP (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def margin(prediction):
    points = 0
    if (
        prediction.tournament_winning_team == team_one
        and prediction.win_series_margin == win_series_margin
    ):
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = "Picked correct win series margin (+2000)"
        tps.points = 2000
        points = tps.points
        tps.save()

    return points


def get_entry(member, entries):
    if entries is None:
        return

    for e in entries:
        if e.member == member:
            return e


def create_tournament_leaderboard(match, tournament_format, board, group, entries):
    previous_match = Match.objects.filter(
        tournament=match.tournament,
        match_type=match.match_type,
        match_number=match.match_number - 1,
    ).first()

    try:
        previous_board = GroupLeaderBoard.objects.get(
            match=previous_match, member_group=group
        )

    except GroupLeaderBoard.DoesNotExist:
        return

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
            le.total = le.tournament_predictions_score

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
    tournament = Tournament.objects.get(id=11)
    tournament_format = Match.T_TWENTY

    # clear old scores
    for tps in TouramentPredictionScore.objects.filter(
        prediction__tournament=tournament,
        prediction__prediction_format=tournament_format,
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
            member_group=member_group,
            tournament=tournament,
            prediction_format=tournament_format,
        ).all():
            points = 0
            points = points + teams(prediction)
            points = points + batsman(prediction)
            points = points + bowler(prediction)
            points = points + mvp(prediction)
            points = points + margin(prediction)

            leaderboard_entry = LeaderBoardEntry()
            leaderboard_entry.leader_board = board
            leaderboard_entry.member = prediction.member
            leaderboard_entry.this_match = 0
            leaderboard_entry.tournament_predictions_score = points
            leaderboard_entry.save()
            le_cache.append(leaderboard_entry)

        create_tournament_leaderboard(
            fake_match, tournament_format, board, member_group, le_cache
        )


"""
import datetime
t = Tournament.objects.get(id=11)
v = Venue.objects.get(id=42)
m = Match()
md = '11/11/2019'

m.tournament = t
m.match_number = 4
m.name = 'IND vs. BAN 2019 T-20, Final Scores: pre-Tournament Predictions + Match Predictions'
m.short_display_name = 'IND vs. BAN 2019 T-20, Final Scores'
m.fake_match = True
m.match_date = datetime.datetime.strptime(md, '%d/%m/%Y')
m.match_type = Match.T_TWENTY
m.match_status = Match.COMPLETED
m.venue = v
m.save()
m.id

"""
