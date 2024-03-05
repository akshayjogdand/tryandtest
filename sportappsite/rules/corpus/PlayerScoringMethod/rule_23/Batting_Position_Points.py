# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 0
rule_category = 0

# T_TWENTY
apply_to_match_type = 2

variables = ("batting_performance", "rule")

enable_for_matches = lambda match: True


def batting_position_points(was_out, position):
    if was_out == 3:
        return 0
    if was_out == 2 and position < 8:
        return 40
    if was_out == 2 and position >= 8:
        return 20
    if was_out == 1 and position < 8:
        return -20
    if was_out == 1 and position >= 8:
        return -5


calculation = lambda: batting_position_points(
    batting_performance.was_out, batting_performance.position
)
