from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from fixtures.models import Match

from members.models import GroupLeaderBoard, MemberGroup

from members.scoring import create_leaderboard


class ComputeLeaderboardCommand(BaseCommand):
    help = "Generate a Leaderboard for a Member Group after a Match"

    def add_arguments(self, parser):
        parser.add_argument("--group-id", type=int, required=True, help="Group ID")
        parser.add_argument("--match-id", type=int, required=True, help="Match ID")

    @transaction.atomic
    def handle(self, match_id, group_id, *args, **kwargs):
        try:
            match = Match.objects.get(id=match_id)
            group = MemberGroup.objects.get(id=group_id)
        except Match.DoesNotExist:
            raise CommandError("Match with ID: {} does not exist.".format(match_id))
        except MemberGroup.DoesNotExist:
            raise CommandError(
                "Member Group with ID: {} does not " "exist.".format(group_id)
            )

        try:
            board = GroupLeaderBoard.objects.filter(
                match=match, member_group=group
            ).first()
        except GroupLeaderBoard.DoesNotExist:
            board = create_leaderboard(match, group, None)
        else:
            create_leaderboard(match, group, board)
