
import logging

from django.db.models.signals import post_save

from django.utils import timezone

from django.dispatch import receiver

from django_q.models import Schedule

from predictions.management.commands.convert_to_tournament_predictions import (
    Command as ConvertSubmissionsCommand,
)

from fixtures.models import TournamentFormats

from scoring.management.commands.score_multi_team_t20_series import (
    Command as MultiLeagueT20SeriesScoringCommand,
)

from scoring.management.commands.score_bi_lateral_odi_series import (
    Command as BiLateralODISeriesScoringCommand,
)

from scoring.management.commands.score_bi_lateral_t20_series import (
    Command as BiLateralT20SeriesScoringCommand,
)

from scoring.management.commands.score_bi_lateral_test_series import (
    Command as BiLateralTestSeriesScoringCommand,
)

from scoring.management.commands.score_t20_wc import (
    Command as ScoreT20WCCommand,
)

from ..models import ScoreSeries

logger = logging.getLogger("auto_jobs")


@receiver(post_save, sender=ScoreSeries)
def score_series_saved(sender, instance, created, **kwargs):
    if instance.execute:
        jr = lodge_score_match_job(instance.id)
        state = instance.state_string(jr)
        instance.job_refs = f"{instance.job_refs}\n{state}"
        instance.execute = False
        instance.save()


def lodge_score_match_job(job_id):
    s = Schedule.objects.create(
        func="auto_jobs.signals.score_series.score_series_job",
        args=(job_id,),
        schedule_type=Schedule.ONCE,
        next_run=timezone.now(),
    )

    return s.id


def score_series_job(job_id):
    j = ScoreSeries.objects.get(id=job_id)
    logger.info(f"Beginning ScoreSeries job, ID={job_id}.")

    if j.convert_predictions:
        logger.info("Converting Series Predictions.")
        cp = ConvertSubmissionsCommand()
        cp.handle(j.tournament.id, j.series)

    if j.leaderboards:
        logger.info("Scoring Series Predictions and Leaderboards.")
        sc = score_command(j.tournament, j)
        sc.handle(j.tournament.id)

    logger.info(f"Finished ScoreSeries job, ID={job_id}.")

    j.reset_job()
    j.save()


def score_command(tournament, score_series_job):
    if tournament.bi_lateral and score_series_job.series == TournamentFormats.ONE_DAY:
        return BiLateralODISeriesScoringCommand()

    elif (
        tournament.bi_lateral and score_series_job.series == TournamentFormats.T_TWENTY
    ):
        return BiLateralT20SeriesScoringCommand()

    elif tournament.bi_lateral and score_series_job.series == TournamentFormats.TEST:
        return BiLateralTestSeriesScoringCommand()

    elif score_series_job.score_t20_wc:
        return ScoreT20WCCommand()

    return MultiLeagueT20SeriesScoringCommand()
