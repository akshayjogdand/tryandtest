from django.db.models.signals import post_save, m2m_changed

from django.db import transaction

from django.dispatch import receiver

from fixtures.models import Tournament

from predictions.utils import create_or_update_submission_config_for_tournament

from ..models import MemberGroup

from ..utils import get_or_create_group_rules_from_defaults

from ..schedules import add_currently_active_tournaments_schedule


@transaction.atomic
@receiver(post_save, sender=MemberGroup)
def new_group_created(sender, instance, created, **kwargs):
    if created:
        add_currently_active_tournaments_schedule(instance)


@transaction.atomic
@receiver(m2m_changed, sender=MemberGroup.tournaments.through)
def new_tournament_configured_for_group(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for t_id in pk_set:
            tournament = Tournament.objects.get(id=t_id)
            get_or_create_group_rules_from_defaults(instance, tournament)
            create_or_update_submission_config_for_tournament(instance, tournament)
