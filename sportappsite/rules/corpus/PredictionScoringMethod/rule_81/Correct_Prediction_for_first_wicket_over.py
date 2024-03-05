# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if prediction.predicted_first_wicket_gone_in_over == match.first_wicket_gone_in_over
    else 0
)
