import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from predictions.models import MemberPrediction, MemberSubmission

from members.models import Member, MemberGroup

logger = logging.getLogger("predictions_conversions")


class Command(BaseCommand):
    help = "Turn all Member Submissions into Match Predictions"

    def add_arguments(self, parser):
        parser.add_argument("--member-id", required=True, type=int, help="MemberID")

        parser.add_argument(
            "--from-group-id", required=True, type=int, help="From Group ID"
        )

        parser.add_argument(
            "--to-group-id", required=True, type=int, help="To Group ID"
        )

    @transaction.atomic
    def handle(self, member_id, from_group_id, to_group_id, **options):

        member = Member.objects.get(id=member_id)
        from_group = MemberGroup.objects.get(id=from_group_id)
        to_group = MemberGroup.objects.get(id=to_group_id)

        old_group_submissions = MemberSubmission.objects.filter(
            member=member,
            member_group=from_group,
            submission_type=MemberSubmission.MATCH_DATA_SUBMISSION,
        )

        for s in old_group_submissions:
            new_sub = MemberSubmission.objects.filter(
                member=member,
                member_group=to_group,
                submission_type=MemberSubmission.MATCH_DATA_SUBMISSION,
                match=s.match,
            )
            if not new_sub.exists():
                logger.info("Converting for: {}".format(s))
                s.id = None
                s.pk = None
                s.member_group = to_group
                s.save()
                logger.info("Converted to: {}".format(s))

        old_group_predictions = MemberPrediction.objects.filter(
            member=member, member_group=from_group
        )

        for p in old_group_predictions:
            try:
                new_pred = MemberPrediction.objects.get(
                    member=member, member_group=to_group, match=p.match
                )
            except MemberPrediction.DoesNotExist:
                logger.info("Converting for: {}".format(p))
                p.id = None
                p.pk = None
                p.member_group = to_group
                p.save()
                logger.info("Converted to: {}".format(p))
