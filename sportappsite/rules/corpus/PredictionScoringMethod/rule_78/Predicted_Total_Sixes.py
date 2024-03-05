# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 400
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if (
        (match.first_innings_sixes + match.second_innings_sixes)
        == prediction.total_sixes
    )
    else 0
)
