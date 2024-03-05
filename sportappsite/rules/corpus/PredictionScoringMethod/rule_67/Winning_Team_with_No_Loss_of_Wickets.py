# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "prediction", "match")

enable_for_matches = lambda match: True


def winning_team_with_no_loss_of_wickets(match, prediction):
    if match.winning_team is None:
        return False
    if match.winning_team.team != prediction.predicted_winning_team:
        return False
    else:
        if prediction.predicted_winning_team == match.bat_first_team.team:
            return match.first_innings_wickets == 0
        else:
            return match.second_innings_wickets == 0


calculation = (
    lambda: rule.points_or_factor
    if winning_team_with_no_loss_of_wickets(match, prediction)
    else 0
)
