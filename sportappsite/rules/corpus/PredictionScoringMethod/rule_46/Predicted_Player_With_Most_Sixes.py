# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if (prediction.player_with_most_sixes in list(match.max_sixes_by.all()))
    else 0
)
