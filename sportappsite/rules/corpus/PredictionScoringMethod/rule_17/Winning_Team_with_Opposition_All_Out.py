# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 100
rule_category = 4

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "prediction", "match")

enable_for_matches = lambda match: True


def winning_team_and_opp_all_out(match, prediction):
    if match.winning_team is None:
        return 0

    if match.team_one.team == prediction.predicted_winning_team:
        opp_team = match.team_two.team
    else:
        opp_team = match.team_one.team

    if match.winning_team.team == prediction.predicted_winning_team:
        return prediction.was_all_out(opp_team)
    else:
        return 0


calculation = (
    lambda: 4 * rule.points_or_factor
    if winning_team_and_opp_all_out(match, prediction)
    else 0
)
