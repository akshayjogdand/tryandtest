from django.db.models.signals import post_save

from django.db import transaction

from django.dispatch import receiver

from configurations.models import Feature

from ..management.commands.create_initial_reward_pool import Command


@transaction.atomic
@receiver(post_save, sender=Feature)
def enable_group_reward(sender, instance, created, **kwargs):
    if instance.feature_type == Feature.FEATURE_GROUP_REWARDS:
        if instance.enabled:
            data = eval(instance.data_fn, {})(instance)
            icm = data["individual_contribution_amount"]
            c = Command()
            c.handle(
                instance.tournament.id,
                instance.member_group.id,
                tournament_format=instance.tournament_format,
                individual_contribution_amount=icm,
            )
