import itertools

from .models import LeaderBoardEntry, GroupLeaderBoard

from predictions.models import MemberPrediction

from fixtures.models import Match


def get_entry(member, entries):
    if entries is None:
        return

    for e in entries:
        if e.member == member:
            return e


def create_leaderboard(match, group, board):

    if board is None:
        board = GroupLeaderBoard()
        board.member_group = group
        board.match = match
        board.save()
    else:
        for le in LeaderBoardEntry.objects.filter(leader_board=board):
            le.delete()

    try:
        previous_match = Match.objects.get(
            tournament=match.tournament,
            match_type=match.match_type,
            match_number=match.match_number - 1,
        )
        previous_board = GroupLeaderBoard.objects.get(
            match=previous_match, member_group=group
        )
        previous_board_entries = list(previous_board.entries.all())
    except (Match.DoesNotExist, GroupLeaderBoard.DoesNotExist):
        previous_board = None
        previous_board_entries = None

    le_cache = []
    for prediction in MemberPrediction.objects.filter(member_group=group, match=match):

        le = LeaderBoardEntry()
        le.leader_board = board
        le.member = prediction.member
        le.this_match = prediction.total_prediction_score
        le.total = prediction.total_prediction_score

        previous_entry = get_entry(prediction.member, previous_board_entries)
        if previous_entry is not None:
            le.previous_points = previous_entry.total
            le.previous_position = previous_entry.position_now
            le.total = le.total + previous_entry.total
        else:
            le.previous_points = 0
            le.previous_position = 0

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

    board.board_number = match.match_number
    board.save()
    return board
