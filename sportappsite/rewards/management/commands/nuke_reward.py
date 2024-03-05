from django.core.management.base import BaseCommand

from django.db import transaction

from ...models import TournamentReward, TournamentRewardParticipant


class Command(BaseCommand):
    help = "Delete a Tournament Reward configuration."

    def add_arguments(self, parser):
        parser.add_argument("--reward-id", required=True, type=int, help="Reward ID")

    @transaction.atomic
    def handle(self, reward_id, **kwargs):
        tr = TournamentReward.objects.get(id=reward_id)
        for trp in TournamentRewardParticipant.objects.filter(reward=tr):
            trp.delete()
        for t_ag in tr.agreement_records.all():
            t_ag.delete()
        tr.delete()
