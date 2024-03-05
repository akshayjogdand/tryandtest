from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from members.models import MemberGroup, GroupLeaderBoard

from predictions.models import (
    MemberTournamentPrediction,
    MemberPrediction,
    MemberSubmission,
)

from fixtures.models import Tournament


class Command(BaseCommand):
    help = "Copy Memberships from + old groups to 1 new group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--to-group", required=True, type=int, help="Destination Group ID"
        )

        parser.add_argument(
            "--from-group",
            required=True,
            type=int,
            dest="from_group",
            action="append",
            help="Source Group IDs",
        )

        parser.add_argument(
            "--tournament-id",
            type=int,
            required=True,
            help="ID for Tournament whose data is supposed to be copied.",
        )

    @transaction.atomic
    def handle(self, to_group, from_group, tournament_id, **kwargs):

        dest = MemberGroup.objects.get(id=to_group)
        t = Tournament.objects.get(id=tournament_id)

        for mid in from_group:
            mg = MemberGroup.objects.get(id=mid)

            print(mg)
            print("\t\tPreds")
            for p in MemberPrediction.objects.filter(
                member_group=mg, match__tournament=t
            ):
                try:
                    MemberPrediction.objects.get(
                        member_group=dest,
                        member=p.member,
                        match__tournament=t,
                        match=p.match,
                    )
                except MemberPrediction.DoesNotExist:
                    x = str(p)
                    p.id = None
                    p.pk = None
                    p.member_group = dest
                    p.save()
                    print("migrated {} to:: {}".format(x, p))

            print("\t\tT-preds")
            for p in MemberTournamentPrediction.objects.filter(
                member_group=mg, tournament=t
            ):
                try:
                    MemberTournamentPrediction.objects.get(
                        member_group=dest,
                        member=p.member,
                        prediction_format=p.prediction_format,
                        tournament=t,
                    )
                except MemberTournamentPrediction.DoesNotExist:
                    x = str(p)
                    p.id = None
                    p.pk = None
                    p.member_group = dest
                    p.save()
                    print("migrated {} to:: {}".format(x, p))

            print("\t\tMember Submissions")
            for p in MemberSubmission.objects.filter(member_group=mg, tournament=t):

                x = str(p)
                p.id = None
                p.pk = None
                p.member_group = dest
                p.save()
                print("migrated {} to:: {}".format(x, p))

            print("\t\tLeaderboards")
            for p in GroupLeaderBoard.objects.filter(
                member_group=mg, match__tournament=t
            ):
                try:
                    GroupLeaderBoard.objects.get(member_group=dest, match=p.match)
                except GroupLeaderBoard.DoesNotExist:
                    x = str(p)
                    p.id = None
                    p.pk = None
                    p.member_group = dest
                    p.save()
                    print("migrated {} to:: {}".format(x, p))
