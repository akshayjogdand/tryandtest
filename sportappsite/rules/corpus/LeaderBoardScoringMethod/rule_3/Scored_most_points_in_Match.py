# LEADERBOARD_SCORING
apply_rule_at = 4

points_or_factor = 2000
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "current_leaderboard", "prediction")

enable_for_matches = lambda match: True


def is_topper(leaderboard, prediction):
    top_score = leaderboard.top_score()
    entry = leaderboard.entry(prediction.member)
    if top_score != 0 and top_score == entry.this_match:
        return True
    else:
        return False


calculation = (
    lambda: rule.points_or_factor if is_topper(current_leaderboard, prediction) else 0
)
