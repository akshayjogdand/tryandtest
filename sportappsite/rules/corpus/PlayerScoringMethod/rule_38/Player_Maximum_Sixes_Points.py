# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 25
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("rule", "player_match_stats")

enable_for_matches = lambda match: True


None
calculation = lambda: rule.points_or_factor if player_match_stats.max_sixes_hit else 0
