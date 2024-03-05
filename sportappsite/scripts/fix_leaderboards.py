from django.db import transaction

from members.models import MemberGroup, GroupLeaderBoard, LeaderBoardEntry

from fixtures.models import Match

GROUPS = [9, 10, 11, 12, 21, 23, 24, 25, 26, 27]

final_match = Match.objects.get(id=89)


@transaction.atomic
def run(*args):
    for gid in GROUPS:
        member_group = MemberGroup.objects.get(id=gid)
        board = GroupLeaderBoard.objects.get(
            member_group=member_group, match=final_match
        )
        for le in LeaderBoardEntry.objects.filter(leader_board=board):
            le.total = le.previous_points + le.this_match
            le.tournament_predictions_score = None
            le.save()
