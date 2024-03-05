# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 30
rule_category = 0

# TEST
apply_to_match_type = 3

variables = ("batting_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: int(batting_performance.runs / 50) * rule.points_or_factor
