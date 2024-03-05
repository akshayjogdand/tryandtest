import logging

from django.db.models.signals import post_save

from django.utils import timezone

from django.dispatch import receiver

from django_q.models import Schedule

from live_scores.models import Properties
from live_scores.management.commands.season_details import (
    Command as SeasonDetailsCommand,
)

from fixtures.management.commands.adjust_tournament_data import (
    Command as AdjustTournamentDataCommand,
)

from members.management.commands.add_tournament_to_all_member_groups import (
    Command as AddTournamentToMemberGroupsCommand,
)

from ..models import FetchSeries

logger = logging.getLogger("auto_jobs")


@receiver(post_save, sender=FetchSeries)
def fetch_series_saved(sender, instance, created, **kwargs):
    if instance.execute:
        jr = lodge_fetch_series_job(instance)
        state = instance.state_string(jr)
        instance.job_refs = f"{instance.job_refs}\n{state}"
        instance.execute = False
        instance.save()


def lodge_fetch_series_job(instance):
    s = Schedule.objects.create(
        func="auto_jobs.signals.fetch_series.fetch_series_job",
        args=(instance.id,),
        schedule_type=Schedule.ONCE,
        next_run=timezone.now(),
    )

    return s.id


def fetch_series_job(instance_id):
    fs = FetchSeries.objects.get(id=instance_id)
    logger.info(f"FetchSeries job, ID={instance_id}.")

    if fs.pull_data:
        logger.info(f"Pulling data, key={fs.series_key}")
        sd = SeasonDetailsCommand()
        sd.handle(season_key=(fs.series_key,))

    if fs.adjust_tournament_data:
        tournament = Properties.get_obj_cricketapi(fs.series_key).first().tournament
        logger.info("Adjusting Tournament Data: Names, Dates, Rules, Config.")
        atd = AdjustTournamentDataCommand()
        atd.handle(tournament.id)

    if fs.add_to_all_groups:
        tournament = Properties.get_obj_cricketapi(fs.series_key).first().tournament
        logger.info(f"Adding {tournament} to all Member Groups")
        atm = AddTournamentToMemberGroupsCommand()
        atm.handle(tournament.id)

    fs.reset_job()
    fs.save()
