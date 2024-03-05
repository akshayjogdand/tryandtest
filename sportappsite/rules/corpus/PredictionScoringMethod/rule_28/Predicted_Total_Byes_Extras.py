# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if ((match.first_innings_byes + match.second_innings_byes) == prediction.total_byes)
    else 0
)
