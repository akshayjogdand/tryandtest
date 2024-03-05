# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def wicket_range_points(rule, prediction, match):
    award = 0

    if not prediction.was_submitted():
        return award

    if prediction.no_pre_toss_submission():
        return award

    tw = match.first_innings_wickets + match.second_innings_wickets

    if tw == prediction.total_wickets:
        award = 300

    elif abs(tw - prediction.total_wickets) == 1:
        award = 100

    elif abs(tw - prediction.total_wickets) == 2:
        award = 50

    return award * rule.points_or_factor


calculation = lambda: wicket_range_points(rule, prediction, match)
