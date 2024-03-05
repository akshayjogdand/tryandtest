# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 400
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("rule", "player_match_stats")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: (player_match_stats.man_of_the_match and rule.points_or_factor) or 0
)
