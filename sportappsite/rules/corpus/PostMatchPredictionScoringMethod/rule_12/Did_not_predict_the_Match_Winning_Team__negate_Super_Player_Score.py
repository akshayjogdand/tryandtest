# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("match", "prediction", "rule", "match_player_scores")

enable_for_matches = lambda match: True


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def negate_super_player_score(prediction, mps):
    if prediction.no_pre_toss_submission():
        return 0

    penalty = 0

    if prediction.super_player_score is not None:
        penalty = -1 * prediction.super_player_score

    #        if prediction.super_player == highest_scoring_player(mps):
    #            penalty = penalty + (-4 * prediction.super_player_score)

    return penalty


calculation = (
    lambda: negate_super_player_score(prediction, match_player_scores)
    if match.winning_team.team != prediction.predicted_winning_team
    else 0
)
