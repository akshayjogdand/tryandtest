# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 50
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "player_match_stats")

enable_for_matches = lambda match: True


None
calculation = lambda: rule.points_or_factor if player_match_stats.most_runs else 0
