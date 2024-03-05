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
    if ((match.first_innings_lbws + match.second_innings_lbws) == prediction.total_lbws)
    else 0
)
