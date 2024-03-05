# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 2
rule_category = 0

# ONE_DAY
apply_to_match_type = 1

variables = ("batting_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: batting_performance.fours * rule.points_or_factor
