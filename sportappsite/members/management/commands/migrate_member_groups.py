from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import MemberGroup, Membership


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
            help="Source Group ID",
        )

    @transaction.atomic
    def handle(self, to_group, from_group, **kwargs):

        dest = MemberGroup.objects.get(id=to_group)

        for mid in from_group:
            mg = MemberGroup.objects.get(id=mid)
            for m in Membership.objects.filter(member_group=mg):
                print(m)
                try:
                    nm = Membership.objects.get(member=m.member, member_group=dest)
                except Membership.DoesNotExist:
                    nm = Membership()
                    nm.member_group = dest
                    nm.member = m.member
                    nm.save()
                    print("Migrated {} from {} to {}".format(m.member, mg, dest))
