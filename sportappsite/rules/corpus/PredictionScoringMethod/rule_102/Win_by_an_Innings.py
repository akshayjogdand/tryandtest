# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 500
rule_category = 4

# TEST
apply_to_match_type = 3

variables = ("match", "prediction", "rule")

enable_for_matches = lambda match: True


def won_by_innings(rule, match, prediction):

    # MR_WIN
    if match.match_result != 0:
        return 0

    if match.fourth_innings_overs != 0 and match.fourth_innings_balls != 0:
        return 0

    winner = match.winning_team.team

    if winner == match.team_one.team:
        if prediction.predicted_winning_team == winner:
            return rule.points_or_factor

    if winner == match.team_two.team:
        if prediction.predicted_winning_team == winner:
            return rule.points_or_factor

    return 0


calculation = lambda: won_by_innings(rule, match, prediction)
