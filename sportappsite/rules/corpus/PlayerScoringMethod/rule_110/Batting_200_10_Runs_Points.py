# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 25
rule_category = 0

# TEST
apply_to_match_type = 3

variables = ("rule", "batting_performance")

enable_for_matches = lambda match: True


def twohundred_plus_extra_ten_runs_points(runs):
    if runs > 200:
        points = math.floor((runs - 200) / 10)
        return points
    else:
        points = 0
        return points


calculation = (
    lambda: twohundred_plus_extra_ten_runs_points(batting_performance.runs)
    * rule.points_or_factor
)
