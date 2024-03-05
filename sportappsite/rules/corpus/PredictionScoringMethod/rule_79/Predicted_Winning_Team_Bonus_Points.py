# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 150
rule_category = 4

# ONE_DAY
apply_to_match_type = 1

variables = ("match", "prediction", "rule")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: rule.points_or_factor
    if (
        match.winning_team is not None
        and (match.winning_team.team == prediction.predicted_winning_team)
        and match.bonus_applicable
    )
    else 0
)
