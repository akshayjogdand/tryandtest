from django.db.models.signals import post_save, m2m_changed
from django.db import transaction

from django.dispatch import receiver

from predictions.models import GroupSubmissionsConfig

from ..models import ConfigItem, Feature


@transaction.atomic
@receiver(post_save, sender=ConfigItem)
def config_item_saved(sender, instance, **kwargs):
    if instance.name.strip() == "match_prediction_notes_text":
        text = instance.value
        for g in GroupSubmissionsConfig.objects.filter(
            tournament=instance.tournament,
            submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
        ):
            g.submission_notes = text
            g.save()


# @transaction.atomic
# @receiver(m2m_changed, sender=Feature.tournaments.through)
# def feature_saved(sender, instance, action, pk_set, **kwargs):
# if action == 'post_save':
# for t_id in pk_set:
# tournament = Tournament.objects.get(id=t_id)
