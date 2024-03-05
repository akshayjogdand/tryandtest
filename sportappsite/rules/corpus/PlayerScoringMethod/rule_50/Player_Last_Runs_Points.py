# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 25
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("player_match_stats", "rule")

enable_for_matches = lambda match: True


None
calculation = lambda: player_match_stats.last_run and rule.points_or_factor or 0
