# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 500
rule_category = 1

# T_TWENTY
apply_to_match_type = 2

variables = ("bowling_performance", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: bowling_performance.hat_tricks * rule.points_or_factor
