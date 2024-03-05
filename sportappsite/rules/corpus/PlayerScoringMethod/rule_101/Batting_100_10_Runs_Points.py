# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 10
rule_category = 0

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "batting_performance")

enable_for_matches = lambda match: True


def hundred_plus_extra_runs_points(runs):
    if runs > 100:
        points = math.floor((runs - 100) / 10)
        return points
    else:
        points = 0
        return points


calculation = (
    lambda: hundred_plus_extra_runs_points(batting_performance.runs)
    * rule.points_or_factor
)
