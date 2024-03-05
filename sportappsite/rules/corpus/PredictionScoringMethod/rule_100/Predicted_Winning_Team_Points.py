# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 500
rule_category = 4

# TEST
apply_to_match_type = 3

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

    # MR_TIE, MR_DRAW -- 23 is draw_team()
    if (match.match_result == 1) or (match.match_result == 2):
        if prediction.predicted_winning_team.id == 23:
            return rule.points_or_factor

    return 0


calculation = lambda: winning_team_points(rule, match, prediction)
