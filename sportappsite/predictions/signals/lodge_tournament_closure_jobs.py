import logging

from datetime import timedelta

from django_q.models import Schedule

from django.db.models.signals import pre_save

from django.db import transaction

from django.dispatch import receiver

from ..models import ControlledGroupSubmissionsConfig


logger = logging.getLogger("predictions_conversions")


@receiver(pre_save, sender=ControlledGroupSubmissionsConfig)
def lodge_convert_predictions_job(sender, instance, update_fields, **kwargs):
    if (
        instance.submission_type
        == ControlledGroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION
    ):

        tid = f"tournament_id={instance.tournament.id}"
        name = f"{tid} Preds Conv. for Tournament:{instance.tournament.name}, format={instance.tournament_format}"

        if len(name) >= 100:
            new_name = name[:95]
            logger.info(f"Truncated job name from: {name} to {new_name}")
            name = new_name

        if not instance.active_to:
            instance.active_to = instance.tournament.start_date

        nr = instance.active_to + timedelta(minutes=1)

        try:
            job = Schedule.objects.get(name__icontains=tid)
            job.next_run = nr
            job.save()

        except Schedule.DoesNotExist:
            job = Schedule.objects.create(
                func="predictions.management.commands.convert_to_tournament_predictions.convert",
                args=(instance.tournament.id, instance.tournament_format),
                name=name,
                schedule_type=Schedule.ONCE,
                next_run=nr,
            )

        logger.info(f"Lodged a Schedule to: {name}, running at: {job.next_run}")
