from django.core.management.base import BaseCommand
from members.models import Member, Membership, MemberVerification, LeaderBoardEntry
from predictions.models import (
    MemberPrediction,
    MemberSubmission,
    MemberTournamentPrediction,
    TouramentPredictionScore,
)
from rewards.models import TournamentRewardParticipant, TournamentRewardAgreement


class Command(BaseCommand):
    help = "remove member"

    def add_arguments(self, parser):
        parser.add_argument(
            "--members-id",
            required=False,
            type=str,
            help="id to use to make member verified. you can pass multiple id with comma",
        )
        parser.add_argument(
            "--members-login",
            required=False,
            type=str,
            help="email to use to make member verified. you can pass multiple email with comma",
        )

    def handle(self, members_id, members_login, *args, **kwargs):
        if members_id is None and members_login is None:
            print("No param passed")
            return
        print("Removed: ")
        if members_id is not None:
            members_id = members_id.split(",")
            members_id = [int(m) for m in members_id]
            members = Member.objects.filter(id__in=members_id)
        if members_login is not None:
            members_login = members_login.split(",")
            members = Member.objects.filter(user__email__in=members_login)
        for member in members:

            # remove from group
            Membership.objects.filter(member=member).delete()
            MemberVerification.objects.filter(member=member).delete()
            LeaderBoardEntry.objects.filter(member=member).delete()

            # remove from predictions
            MemberSubmission.objects.filter(member=member).delete()
            MemberPrediction.objects.filter(member=member).delete()
            TouramentPredictionScore.objects.filter(prediction__member=member).delete()
            MemberTournamentPrediction.objects.filter(member=member).delete()

            # remove from stat
            # MemberStat - member stat will change if you delete member here

            # Payments
            # when app merged

            # remove from rewartds
            TournamentRewardParticipant.objects.filter(member=member).delete()
            TournamentRewardAgreement.objects.filter(admin_member=member).delete()

            print(member)
            user = member.user
            member.delete()
            user.delete()
