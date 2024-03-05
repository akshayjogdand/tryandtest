# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 40
rule_category = 1

# ONE_DAY
apply_to_match_type = 1

variables = ("bowling_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: bowling_performance.wickets * rule.points_or_factor
