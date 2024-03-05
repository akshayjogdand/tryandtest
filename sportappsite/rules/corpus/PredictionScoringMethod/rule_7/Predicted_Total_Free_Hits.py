# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "prediction", "match")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if (
        prediction.total_free_hits
        == (match.first_innings_free_hits + match.second_innings_free_hits)
    )
    else 0
)
