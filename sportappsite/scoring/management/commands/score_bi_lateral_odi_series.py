import logging
import itertools

from datetime import timedelta

from django.core.management.base import BaseCommand

from django.db import transaction

from fixtures.models import Tournament, Match

from members.models import LeaderBoardEntry, GroupLeaderBoard

from predictions.models import MemberTournamentPrediction, TouramentPredictionScore

from auto_jobs.models import ScoreSeries

logger = logging.getLogger("score_bi_lateral_odi_series")


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
    finalists = (j.winner, j.runner_up)

    return finalists


def get_entry(member, entries):
    if entries is None:
        return

    for e in entries:
        if e.member == member:
            return e


def player_of_the_tournament(prediction, player_of_the_tournament):
    points = 0

    if player_of_the_tournament in (
        prediction.player_of_the_tournament_one,
        prediction.player_of_the_tournament_two,
    ):
        points = 2000
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = "Picked Player of the Tourament (+2000)"
        tps.points = 2000
        tps.player = player_of_the_tournament
        tps.save()

    return points


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

        if player == ranked_mvps[2]:
            tps.rule = "Picked 2nd ranked MVP (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def margin(prediction, finalists, margin):
    points = 0
    if (
        prediction.tournament_winning_team == finalists[0]
        and prediction.win_series_margin == margin
    ):
        tps = TouramentPredictionScore()
        tps.prediction = prediction
        tps.rule = "Picked correct win series margin (+2000)"
        tps.points = 2000
        points = tps.points
        tps.save()

    return points


def batsmen(prediction, ranked_batsmen):
    points = 0
    # batsman
    for player in prediction.batsman_vars().values():
        tps = TouramentPredictionScore()
        tps.prediction = prediction

        if player == ranked_batsmen[1]:
            tps.rule = "Picked Top Run Scorer (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == ranked_batsmen[2]:
            tps.rule = "Picked 2nd best Run Scorer (+500)"
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
            tps.rule = "Picked Player with most Wickets (+1000)"
            points = points + 1000
            tps.points = 1000
            tps.player = player

        if player == ranked_bowlers[2]:
            tps.rule = "Picked Player with 2nd highest Wickets (+500)"
            points = points + 500
            tps.points = 500
            tps.player = player

        if tps.points > 0:
            tps.save()

    return points


def teams(prediction, finalists):
    points = 0

    # picked series winner
    tps = TouramentPredictionScore()
    tps.prediction = prediction
    tps.rule = "Picked Tournament Winner (+2000)"
    if prediction.tournament_winning_team == finalists[0]:
        points = points + 2000
        tps.points = 2000
        tps.team_one = finalists[0]
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
            fake_match=True, tournament=tournament, match_type=Match.ONE_DAY
        )
    except Match.DoesNotExist:
        m = Match()
        m.tournament = tournament
        final_match = (
            tournament.matches.filter(match_type=Match.ONE_DAY)
            .order_by("-match_date")
            .first()
        )
        m.fake_match = True
        m.match_number = final_match.match_number + 1
        m.match_date = final_match.match_date + timedelta(hours=6)
        m.match_type = Match.ONE_DAY
        m.match_status = Match.COMPLETED
        m.assign_final_scores_match_name()
        m.save()

    return m


class Command(BaseCommand):
    help = "Score a Bi-lateral ODI Series"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tourament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)
        j = ScoreSeries.objects.get(tournament=tournament, series=Match.ONE_DAY)

        with transaction.atomic():
            fake_match = get_fake_match(tournament)

        finalists = setup_teams(tournament, j)

        previous_match = (
            Match.objects.filter(
                tournament=fake_match.tournament,
                match_date__date__lte=fake_match.match_date,
                match_type=Match.ONE_DAY,
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
        logger.info(f"Clearing old ODI Series final Leaderboards for {tournament}")
        for tps in TouramentPredictionScore.objects.filter(
            prediction__tournament=tournament,
            prediction__prediction_format=Match.ONE_DAY,
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
                prediction_format=Match.ONE_DAY,
                tournament=tournament,
            ).all():
                points = 0
                points = points + teams(prediction, finalists,)
                points = points + batsmen(prediction, ranked_batsmen)
                points = points + bowlers(prediction, ranked_bowlers)
                points = points + mvp(prediction, ranked_mvps)
                points = points + margin(prediction, finalists, j.win_series_margin)
                points = points + bonuses(prediction, group_bonus, members)
                points = points + player_of_the_tournament(
                    prediction, j.player_of_the_tournament
                )

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
