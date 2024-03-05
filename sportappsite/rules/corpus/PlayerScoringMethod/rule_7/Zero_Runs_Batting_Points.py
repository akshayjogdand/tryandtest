# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 0
rule_category = 0

# T_TWENTY
apply_to_match_type = 2

variables = ("batting_performance",)

enable_for_matches = lambda match: True


def zero_batting_points(was_out, runs, balls, position):
    if runs > 0:
        return 0

    if was_out == 3 or was_out == 2:
        return 0

    if position > 7:
        return 0

    if balls == 0:
        return -20
    if balls == 1:
        return -15
    if balls == 2:
        return -10
    if balls > 2:
        return -5


calculation = lambda: zero_batting_points(
    batting_performance.was_out,
    batting_performance.runs,
    batting_performance.balls,
    batting_performance.position,
)
