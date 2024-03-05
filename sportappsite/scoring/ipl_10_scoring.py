from scoring.management.commands.score_match import Command as ScoreMatchCommand

from predictions.management.commands.score_member_predictions import (
    Command as PredictionScoringCommand,
)


def score_an_ipl_10_match(match_id):
    smc = ScoreMatchCommand()
    smc.handle(match_id=match_id, re_score=True, no_print=True)

    psc = PredictionScoringCommand()
    psc.handle(match_id=match_id)
