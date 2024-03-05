# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 400
rule_category = 4

# ONE_DAY
apply_to_match_type = 1

variables = ("match", "prediction", "rule")

enable_for_matches = lambda match: True


def winning_team_points(rule, match, prediction):
    # MR_UNKNOWN
    if match.match_result == -1:
        return 0

    # MR_WIN
    if match.match_result == 0:
        if match.winning_team.team == prediction.predicted_winning_team:
            return rule.points_or_factor
        else:
            return 0

    # MR_TIE, MR_DRAW, MR_NO_RESULT
    if (
        match.match_result == 1 or match.match_result == 2
    ):  # or match.match_result == 3):
        return 400
    else:
        return 0


calculation = lambda: winning_team_points(rule, match, prediction)
