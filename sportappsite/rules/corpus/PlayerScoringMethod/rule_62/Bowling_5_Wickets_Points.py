# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 150
rule_category = 1

# TEST
apply_to_match_type = 3

variables = ("bowling_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: int(bowling_performance.wickets / 5) * rule.points_or_factor
