# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 15
rule_category = 0

# TEST
apply_to_match_type = 3

variables = ("rule", "batting_performance")

enable_for_matches = lambda match: True


None
calculation = lambda: int(batting_performance.runs / 25) * rule.points_or_factor
