# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def total_fours_range_points(rule, match, prediction):
    award = 0

    if not prediction.was_submitted():
        return award

    if prediction.no_pre_toss_submission():
        return award

    tf = match.first_innings_fours + match.second_innings_fours

    if tf == prediction.total_fours:
        award = 300

    elif abs(tf - prediction.total_fours) == 1:
        award = 100

    elif abs(tf - prediction.total_fours) == 2:
        award = 50

    return award * rule.points_or_factor


calculation = lambda: total_fours_range_points(rule, match, prediction)
