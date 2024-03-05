# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 2
rule_category = 4

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction", "rule")

enable_for_matches = lambda match: True


None
calculation = (
    lambda: (int(prediction.super_player_score) * (rule.points_or_factor - 1))
    if (
        prediction.super_player is not None
        and prediction.super_player_score is not None
    )
    else 0
)
