from django.db.models.signals import post_save, pre_save

from django.db import transaction

from django.dispatch import receiver

from ..models import Tournament, PlayerTournamentHistory

from ..management.commands.adjust_match_data import Command


@transaction.atomic
@receiver(post_save, sender=Tournament)
def adjust_names(sender, instance, update_fields, **kwargs):
    c = Command()
    c.handle(tournament_id=instance.id)


@transaction.atomic
@receiver(pre_save, sender=PlayerTournamentHistory)
def add_player_skill(sender, instance, update_fields, **kwargs):
    instance.player_skill = instance.player.player_skill
