from django.core.management.base import BaseCommand

from ...models import PlayerStat, TeamStat, PredictionFieldStat


class Command(BaseCommand):
    help = "For a given Match dump all stats as text to facilitate comparison if code changes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--match-id",
            required=True,
            type=int,
            help="Match for which Global stats are to be dumped.",
        )

        parser.add_argument(
            "--group-id",
            required=False,
            type=int,
            help="Also include for Member Group.",
        )

    def handle(self, match_id, group_id, **opts):
        print("Global Player Stats")
        print("=========================")
        for ps in PlayerStat.objects.filter(match=match_id, member_group=None).order_by(
            "player__name", "-is_latest"
        ):
            x = (
                ps.player,
                ps.stat_name,
                ps.stat_value,
                f"is_latest: {ps.is_latest}",
            )
            x = [str(i) for i in x]
            print("  ".join(x))
            print("----")

        if group_id:
            print("\n\n\n")
            print("Player Stats for Member Group")
            print("=================================")
            for ps in PlayerStat.objects.filter(
                match=match_id, member_group=group_id
            ).order_by("player__name", "-is_latest"):
                x = (
                    ps.player,
                    ps.stat_name,
                    ps.stat_value,
                    f"is_latest: {ps.is_latest}",
                )
                x = [str(i) for i in x]
                print("  ".join(x))
                print(ps.member_group)
                print("----")

        print("\n\n\n")
        print("Global Team Stats")
        print("=========================")
        for ts in TeamStat.objects.filter(match=match_id, member_group=None).order_by(
            "team__name", "is_latest"
        ):
            x = (ts.team, ts.stat_name, ts.stat_value, f"is_latest: {ts.is_latest}")
            x = [str(i) for i in x]
            print("  ".join(x))
            print("----")

        if group_id:
            print("\n\n\n")
            print("Team Stats for Member Group")
            print("===============================")
            for ts in TeamStat.objects.filter(
                match=match_id, member_group=group_id
            ).order_by("team__name", "-is_latest"):
                x = (ts.team, ts.stat_name, ts.stat_value, f"is_latest: {ts.is_latest}")
                x = [str(i) for i in x]
                print("  ".join(x))
                print("----")

        print("\n\n\n")
        print("Global Range Stats")
        print("=========================")
        for pfs in PredictionFieldStat.objects.filter(
            match=match_id, member_group=None
        ).order_by("team__name", "-is_latest"):
            x = (
                pfs.stat_name,
                pfs.stat_value,
                f"is_latest: {pfs.is_latest}",
            )
            x = [str(i) for i in x]
            print("  ".join(x))
            print("----")

        if group_id:
            print("\n\n\n")
            print("Range Stats for Member Group")
            print("===================================")
            for pfs in PredictionFieldStat.objects.filter(
                match=match_id, member_group=group_id
            ).order_by("team__name", "-is_latest"):
                x = (
                    pfs.stat_name,
                    pfs.stat_value,
                    f"is_latest: {pfs.is_latest}",
                )
                x = [str(i) for i in x]
                print("  ".join(x))
                print(pfs.member_group)
                print("----")
