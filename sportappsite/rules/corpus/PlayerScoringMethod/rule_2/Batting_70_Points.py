# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 90
rule_category = 0

# T_TWENTY
apply_to_match_type = 2

variables = ("batting_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: int(batting_performance.runs / 70) * rule.points_or_factor
