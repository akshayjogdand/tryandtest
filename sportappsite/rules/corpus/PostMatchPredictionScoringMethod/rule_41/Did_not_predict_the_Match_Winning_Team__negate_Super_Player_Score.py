# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 3
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("match", "prediction", "rule")

enable_for_matches = lambda match: True


def negate_super_player_score(prediction, rule):
    if prediction.super_player_score is not None:
        return -rule.points_or_factor * prediction.super_player_score
    else:
        return 0


calculation = (
    lambda: negate_super_player_score(prediction, rule)
    if match.winning_team.team != prediction.predicted_winning_team
    else 0
)
