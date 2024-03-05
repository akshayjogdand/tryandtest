import logging
import itertools

from datetime import timedelta

from django.core.management.base import BaseCommand

from django.db import transaction

from fixtures.models import Tournament, Match

from members.models import LeaderBoardEntry, GroupLeaderBoard

from predictions.models import MemberTournamentPrediction, TouramentPredictionScore

from auto_jobs.models import ScoreSeries

logger = logging.getLogger("score_multi_team_t20_series")

tps_team_vars = ["team_one", "team_two", "team_three", "team_four"]


def setup_batsmen(tournament, j):
    return [
        None,
        j.batsman_one,
        j.batsman_two,
        j.batsman_three,
        j.batsman_four,
        j.batsman_five,
    ]


def setup_bowlers(tournament, j):
    return [
        None,
        j.bowler_one,
        j.bowler_two,
        j.bowler_three,
        j.bowler_four,
        j.bowler_five,
    ]


def setup_mvp(tournament, j):
    return [None, j.mvp_one, j.mvp_two, j.mvp_three, j.mvp_four, j.mvp_five]


def setup_teams(tournament, j):
    winning_teams_by_rank = dict()

    winning_teams_by_rank["top_team_one"] = j.team_one
    winning_teams_by_rank["top_team_two"] = j.team_two
    winning_teams_by_rank["top_team_three"] = j.team_three
    winning_teams_by_rank["top_team_four"] = j.team_four

    finalists = (j.winner, j.runner_up)

    winning_teams_by_team = {v: k for k, v in winning_teams_by_rank.items()}

    return winning_teams_by_rank, winning_teams_by_team, finalists, j.last_team


def get_entry(member, entries):
    if entries is None:
        return

    for e in entries:
        if e.member == member:
            return e


def add_teams(tps, teams):
    vars_to_set = tps_team_vars.copy()
    for team in teams:
        v = vars_to_set.pop(0)
        setattr(tps, v, team)


def mvp(prediction, ranked_mvps):
    points = 0
    players = prediction.mvp_vars().values()
    # MVP

    for player in players:
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == ranked_mvps[1]:
            tps.rule = "Picked Top MVP (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player in (ranked_mvps[2], ranked_mvps[3]):
            tps.rule = "Picked 2nd or 3rd ranked MVP (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player in (ranked_mvps[4], ranked_mvps[5]):
            tps.rule = "Picked 2nd ranked MVP (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def batsmen(prediction, ranked_batsmen):
    points = 0
    # batsman
    for player in prediction.batsman_vars().values():
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == ranked_batsmen[1]:
            tps.rule = "Picked Top Batsman (+1500)"
            points = points + 1500
            tps.points = 1500
            tps.player = player

        if player in (ranked_batsmen[2], ranked_batsmen[3]):
            tps.rule = "Picked 2nd or 3rd ranked Batsman from Top 5 (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player in (ranked_batsmen[4], ranked_batsmen[5]):
            tps.rule = "Picked 4th or 5th ranked Batsman from Top 5 (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def bowlers(prediction, ranked_bowlers):
    points = 0
    # batsman
    for player in prediction.bowler_vars().values():
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == ranked_bowlers[1]:
            tps.rule = "Picked Top Bowler (+1500)"
            points = points + 1500
            tps.points = 1500
            tps.player = player

        if player in (ranked_bowlers[2], ranked_bowlers[3]):
            tps.rule = "Picked 2nd or 3rd ranked Bowler from Top 5 (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player in (ranked_bowlers[4], ranked_bowlers[5]):
            tps.rule = "Picked 4th or 5th ranked Bowler from Top 5 (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def teams(prediction, winning_teams_by_rank, winning_teams_by_team, finalists, last_team):
    points = 0
    correctly_predicted_teams = {
        k: v
        for k, v in prediction.top_team_vars().items()
        if v in winning_teams_by_team
    }

    # picked series winner
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Tournament Winner (+8000)"
    if prediction.tournament_winning_team == finalists[0]:
        points = points + 8000
        tps.points = 8000
        tps.team_one = finalists[0]
        tps.save()

    # picked series runner up
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Runner Up (+4000)"
    if prediction.runner_up == finalists[1]:
        points = points + 4000
        tps.points = 4000
        tps.team_one = finalists[1]
        tps.save()

    # picked finalist in any order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Finalists (+1000 per Team)"
    fp = 0
    fp_teams = []

    if prediction.tournament_winning_team in finalists:
        fp = fp + 1000
        fp_teams.append(prediction.tournament_winning_team)
    if prediction.runner_up in finalists:
        fp = fp + 1000
        fp_teams.append(prediction.runner_up)

    if fp > 0:
        points = points + fp
        tps.points = fp
        add_teams(tps, fp_teams)
        tps.save()

    # picked any team in top 1-4
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked any Team from Top 4 (+500)"
    if len(correctly_predicted_teams) > 0:
        p = len(correctly_predicted_teams) * 500
        points = points + p
        tps.points = p
        add_teams(tps, correctly_predicted_teams.values())
        tps.save()

    # picked any team in top 4, in exact order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked any Team from Top 4, in ranked order (+500 per Team)"
    tp = 0
    tp_teams = []

    for k, v in correctly_predicted_teams.items():
        if v in winning_teams_by_team:
            if k == winning_teams_by_team[v]:
                tp = tp + 500
                tp_teams.append(v)
    if tp > 0:
        points = points + tp
        tps.points = tp
        add_teams(tps, tp_teams)
        tps.save()

    # picked all 4 teams in no order
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked all 4 Top Teams in no order (+2000)"
    if len(correctly_predicted_teams) == 4:
        points = points + 2000
        tps.points = 2000
        tps.team_one = winning_teams_by_rank["top_team_one"]
        tps.team_two = winning_teams_by_rank["top_team_two"]
        tps.team_three = winning_teams_by_rank["top_team_three"]
        tps.team_four = winning_teams_by_rank["top_team_four"]
        tps.save()

    # picked all 4 teams in order:
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked all 4 Top Teams in ranked order (+2000)"
    if (
        prediction.tournament_winning_team == winning_teams_by_rank["top_team_one"]
        and prediction.runner_up == winning_teams_by_rank["top_team_two"]
        and prediction.top_team_three == winning_teams_by_rank["top_team_three"]
        and prediction.top_team_four == winning_teams_by_rank["top_team_four"]
    ):
        points = points + 2000
        tps.points = 2000
        tps.team_one = winning_teams_by_rank["top_team_one"]
        tps.team_two = winning_teams_by_rank["top_team_two"]
        tps.team_three = winning_teams_by_rank["top_team_three"]
        tps.team_four = winning_teams_by_rank["top_team_four"]
        tps.save()

    # picked last team
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Last Team (+2000)"
    if prediction.last_team == last_team:
        points = points + 2000
        tps.points = 2000
        tps.last_team = last_team
        tps.save()

    return points


def bonuses(prediction, bonus, members):
    if bonus is None or members is None:
        return 0

    p = 0

    if prediction.member.id in members:
        print(f"Awarding {prediction}      {bonus}")
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.points = bonus
        tps.rule = "Tournament Bonus Points"
        tps.save()
        p = bonus

    return p


def get_bonus(group, bonus_config):
    for c in bonus_config:
        if c["mg"] == group.id:
            return c["bonus"], c["members"]

    return None, None


def create_tournament_leaderboard(match, board, previous_board, group, entries):
    if previous_board is None:
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
    grouped_by_total = itertools.groupby(le_cache, lambda le: le.total)

    for position, (_, entries) in enumerate(grouped_by_total, 1):
        for le in entries:
            le.position_now = position
            if le.previous_position != 0:
                le.movement = (le.position_now - le.previous_position) * -1
            else:
                le.movement = le.position_now

            if match.match_number == 1:
                le.movement = 0

            le.save()

    board.save()
    return board


def get_fake_match(tournament):
    try:
        m = Match.objects.get(
            fake_match=True, tournament=tournament, match_type=Match.T_TWENTY
        )
    except Match.DoesNotExist:
        m = Match()
        m.tournament = tournament
        final_match = (
            tournament.matches.filter(match_type=Match.T_TWENTY)
            .order_by("-match_date")
            .first()
        )
        m.match_number = final_match.match_number + 1
        m.match_date = final_match.match_date + timedelta(hours=6)
        m.match_type = Match.T_TWENTY
        m.match_status = Match.COMPLETED
        m.fake_match = True
        m.assign_final_scores_match_name()
        m.save()

    return m


class Command(BaseCommand):
    help = "Score a Multi Team T20 Series"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tourament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)
        j = ScoreSeries.objects.get(tournament=tournament, series=Match.T_TWENTY)

        with transaction.atomic():
            fake_match = get_fake_match(tournament)

        (winning_teams_by_rank, winning_teams_by_team, finalists, last_team) = setup_teams(
            tournament, j
        )

        previous_match = (
            Match.objects.filter(
                tournament=fake_match.tournament,
                match_date__date__lte=fake_match.match_date,
                match_type=Match.T_TWENTY,
                fake_match=False,
            )
            .order_by("-match_date")
            .first()
        )

        bonus_config = eval(j.bonus_configuration, {}, {})

        ranked_batsmen = setup_batsmen(tournament, j)
        ranked_bowlers = setup_bowlers(tournament, j)
        ranked_mvps = setup_mvp(tournament, j)

        # clear old scores
        logger.info(f"Clearing old T20 Series final Leaderboards for {tournament}")
        for tps in TouramentPredictionScore.objects.filter(
            prediction__tournament=tournament,
            prediction__prediction_format=Match.T_TWENTY,
        ).all():
            tps.delete()

        for member_group in tournament.participating_member_groups.all():
            le_cache = []
            group_bonus, members = get_bonus(member_group, bonus_config)

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

            try:
                previous_leaderboard = GroupLeaderBoard.objects.get(
                    match=previous_match,
                    member_group=member_group,
                    is_tournament_leaderboard=False,
                )

            except GroupLeaderBoard.DoesNotExist:
                previous_leaderboard = None

            for prediction in MemberTournamentPrediction.objects.filter(
                member_group=member_group,
                prediction_format=Match.T_TWENTY,
                tournament=tournament,
            ).all():
                points = 0
                points = points + teams(
                    prediction, winning_teams_by_rank, winning_teams_by_team, finalists, last_team
                )
                points = points + batsmen(prediction, ranked_batsmen)
                points = points + bowlers(prediction, ranked_bowlers)
                points = points + mvp(prediction, ranked_mvps)
                points = points + bonuses(prediction, group_bonus, members)

                leaderboard_entry = LeaderBoardEntry()
                leaderboard_entry.leader_board = board
                leaderboard_entry.member = prediction.member
                leaderboard_entry.this_match = 0
                leaderboard_entry.tournament_predictions_score = points
                leaderboard_entry.save()
                le_cache.append(leaderboard_entry)

                prediction.total_prediction_score = points

                try:
                    prediction.grand_score = (
                        LeaderBoardEntry.objects.get(
                            leader_board=previous_leaderboard, member=prediction.member
                        ).total
                        + points
                    )
                except LeaderBoardEntry.DoesNotExist:
                    pass

                prediction.save()

            create_tournament_leaderboard(
                fake_match, board, previous_leaderboard, member_group, le_cache,
            )
