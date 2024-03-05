# PLAYER_SCORING
apply_rule_at = 0

points_or_factor = 1
rule_category = 0

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "batting_performance")

enable_for_matches = lambda match: True


def seventy_plus_extra_runs_points(runs):
    if runs > 70:
        points = runs - 70
        return points
    else:
        points = 0
        return points


calculation = (
    lambda: seventy_plus_extra_runs_points(batting_performance.runs)
    * rule.points_or_factor
)
