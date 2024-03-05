# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction", "match")

enable_for_matches = lambda match: True


def negate_player_scores(prediction):
    player_scores = 0

    # None to accomodate Prediction put in after toss -- only 1 player selection allowed, i.e no Team.
    if prediction.predicted_winning_team not in (match.winning_team.team, None):
        for (
            player_var,
            player_score_var,
        ) in prediction.player_vars_to_player_scores_vars().items():
            player_score = getattr(prediction, player_score_var)
            if player_score is not None:
                player_scores = player_scores + player_score.total_score

    return player_scores * -1


calculation = lambda: negate_player_scores(prediction)
