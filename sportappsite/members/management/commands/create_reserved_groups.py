from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import create_reserved_member_group


class Command(BaseCommand):
    help = "Create a reserved Member Group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", required=True, type=int, help="How many to create."
        )

    @transaction.atomic
    def handle(self, count, **kwargs):
        for i in range(count):
            create_reserved_member_group()
