# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 0
rule_category = 1

# T_TWENTY
apply_to_match_type = 2

variables = ("bowling_performance",)

enable_for_matches = lambda match: True


def bowling_economy_points(economy, overs, balls):
    if overs == 0 and balls == 0:
        return 0

    if economy <= 3:
        return 40
    if economy > 3 and economy <= 4:
        return 30
    if economy > 4 and economy <= 5:
        return 20
    if economy > 5 and economy <= 6:
        return 10
    if economy > 6 and economy <= 7:
        return 0
    if economy > 7 and economy <= 8:
        return -10
    if economy > 8 and economy <= 9:
        return -20
    if economy > 9 and economy <= 10:
        return -30
    if economy > 10:
        return -40


calculation = lambda: bowling_economy_points(
    bowling_performance.economy, bowling_performance.overs, bowling_performance.balls
)
