import logging

from fixtures.models import Match

from scoring.management.commands.score_match import Command as ScoreMatchCommand

from scoring.management.commands.compute_leaderboard import ComputeLeaderboardCommand

from predictions.management.commands.score_member_predictions import (
    Command as PredictionScoringCommand,
)


def prediction_score_match_in_over(match_id, over_id):
    logger = logging.getLogger("prediction_scoring")
    match = Match.objects.get(id=match_id)

    logger.info("Scoring Players, match: {}, over: {} -- begin".format(match, over_id))
    smc = ScoreMatchCommand()
    smc.handle(match_id=match_id, re_score=True, no_print=True)
    logger.info(
        "Scoring Players, match: {}, over: {} -- complete".format(match, over_id)
    )

    logger.info(
        "Scoring Predictions, match: {}, over: {} -- begin".format(match, over_id)
    )
    psc = PredictionScoringCommand()
    psc.handle(match_id=match_id)
    logger.info(
        "Scoring Predictions, match: {}, over: {} -- complete".format(match, over_id)
    )

    for member_group in match.tournament.participating_member_groups.all():
        logger.info(
            "Computing Leaderboard, member group: {}, "
            "match: {}, over: {} -- begin".format(member_group, match, over_id)
        )
        clbd = ComputeLeaderboardCommand()
        clbd.handle(match.id, member_group.id)
        logger.info(
            "Computing Leaderboard, member group: {}, "
            "match: {}, over: {} -- complete".format(member_group, match, over_id)
        )


def scoring_complete(task):
    logger = logging.getLogger("prediction_scoring")
    logger.info("{} complete.".format(task.group))


"""
Example of Schedule to kick off the process.

    Schedule.objects.create(
        func='scoring.score_predictions_in_live_match.prediction_score_match_in_over',
        hook='scoring.score_predictions_in_live_match.scoring_complete',
        args=('74', '11'),
        name='Live Predictions Scoring, over=11',
        schedule_type=Schedule.ONCE)
"""
