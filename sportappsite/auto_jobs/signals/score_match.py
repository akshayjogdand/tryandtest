import logging

from django.db.models.signals import post_save

from django.utils import timezone

from django.dispatch import receiver

from django_q.models import Schedule

from fixtures.models import Match

from predictions.management.commands.convert_to_predictions import (
    Command as ConvertSubmissionsCommand,
)

from live_scores.models import Properties

from live_scores.management.commands.ball_by_ball import Command as FetchScoresCommand

from live_scores.management.commands.match_completion import (
    Command as FinishMatchCommand,
)

from scoring.management.commands.score_match import Command as ScoreMatchCommand

from predictions.management.commands.score_member_predictions import (
    Command as ScorePredictionsCommand,
)

from stats.management.commands.compute_player_stats import Command as PlayerStatsCommand

from predictions.management.commands.revert_match_prediction_conversions import (
    Command as RevertPredictionConversions,
)

from ..models import ScoreMatch

logger = logging.getLogger("auto_jobs")


@receiver(post_save, sender=ScoreMatch)
def score_match_saved(sender, instance, created, **kwargs):
    if instance.execute:
        jr = lodge_score_match_job(instance.id)
        state = instance.state_string(jr)
        instance.job_refs = f"{instance.job_refs}\n{state}"
        instance.execute = False
        instance.save()


def lodge_score_match_job(job_id):
    s = Schedule.objects.create(
        func="auto_jobs.signals.score_match.score_match_job",
        args=(job_id,),
        schedule_type=Schedule.ONCE,
        next_run=timezone.now(),
    )

    return s.id


def score_match_job(job_id):
    j = ScoreMatch.objects.get(id=job_id)
    logger.info(f"Beginning ScoreMatch job, ID={job_id}.")

    if j.convert_predictions:
        logger.info("Converting Predictions.")
        cp = ConvertSubmissionsCommand()
        cp.handle(j.match.id, True)
        cp.handle(j.match.id, False)

    if j.fetch_scores:
        logger.info("Fetching Match scores.")
        match_key = Properties.objects.get(
            tournament=None, match=j.match, player=None, squad=None, team=None
        ).property_value

        c = FetchScoresCommand()

        c.handle(
            match_key=[match_key],
            over_interval=2,
            start_over=1,
            end_over=20,
            redo=True,
            team=None,
            innings=1,
        )

        if j.match.match_type == Match.TEST:
            c.handle(
                match_key=[match_key],
                over_interval=2,
                start_over=1,
                end_over=20,
                redo=True,
                team=None,
                innings=2,
            )

        fm = FinishMatchCommand()
        fm.handle(match_key=[match_key])

    if j.score_players:
        logger.info("Scoring Players.")
        sm = ScoreMatchCommand()
        sm.handle(j.match.id, True, True)

        logger.info("Computing Player Stats.")
        ps = PlayerStatsCommand()
        ps.handle(j.match.id, True)

    if j.leaderboards:
        logger.info("Scoring Predictions and Leaderboards.")
        sp = ScorePredictionsCommand()
        sp.handle(j.match.id)

    if j.revert_prediction_conversions:
        logger.info("Reverting Predictions conversions.")
        rp = RevertPredictionConversions()
        rp.handle(j.match.id)

    j.reset_job()
    j.save()
