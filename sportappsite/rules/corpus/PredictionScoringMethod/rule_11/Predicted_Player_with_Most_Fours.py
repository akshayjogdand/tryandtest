# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule,match,prediction",)

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if (prediction.player_with_most_fours in list(match.max_fours_by.all()))
    else 0
)
