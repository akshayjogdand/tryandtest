# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 0
rule_category = 0

# TEST
apply_to_match_type = 3

variables = ("batting_performance",)

enable_for_matches = lambda match: True


def strike_rate_points(strike_rate, balls, was_out, batting_position):
    if was_out == 3:
        return 0

    if was_out == 2 and balls == 0:
        return 0

    base_points = 0

    if was_out == 1:
        base_points = strike_rate

    elif was_out == 2 and balls > 0:
        base_points = strike_rate

    if base_points <= 50 and batting_position >= 8 and batting_position <= 11:
        return -5

    if base_points <= 25.0:
        return -15
    if base_points > 25.0 and base_points <= 50.0:
        return -5
    if base_points > 50.0 and base_points <= 65.0:
        return 5
    if base_points > 65.0 and base_points <= 75.0:
        return 10
    if base_points > 75.0 and base_points <= 90.0:
        return 20
    if base_points > 90.0 and base_points <= 120.0:
        return 30
    if base_points > 120.0:
        return 40


calculation = lambda: strike_rate_points(
    batting_performance.strike_rate,
    batting_performance.balls,
    batting_performance.was_out,
    batting_performance.position,
)
