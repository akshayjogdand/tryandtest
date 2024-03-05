# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 50
rule_category = 2

# TEST
apply_to_match_type = 3

variables = ("fielding_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: fielding_performance.runouts * rule.points_or_factor
