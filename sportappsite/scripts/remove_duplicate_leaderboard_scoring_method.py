from django.db import transaction
from rules.models import (
    GroupLeaderBoardScoringMethod,
    LeaderBoardScoringMethod,
    GroupLeaderBoardScoringMethodResult,
)
from members.models import MemberGroup, MemberGroupRules


def run():
    for i in [1, 2, 3]:
        parent = LeaderBoardScoringMethod.objects.get(id=i)
        for mg in MemberGroup.objects.all():
            mgr = MemberGroupRules.objects.get(member_group=mg)
            rules = mgr.group_leaderboard_scoring_rules.filter(
                parent_rule=parent
            ).order_by("id")
            if len(rules) > 1:
                r = rules[1]
                for rr in GroupLeaderBoardScoringMethodResult.objects.filter(
                    rule=r
                ).all():
                    rr.delete()
                print("{} -- Removing {}".format(mg, r))
                r.delete()
