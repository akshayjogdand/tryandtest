# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 100
rule_category = 1

# TEST
apply_to_match_type = 3

variables = ("rule", "bowling_performance")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor * (bowling_performance.wickets - 4)
    if (bowling_performance.wickets - 4 > 0)
    else 0
)
