# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def total_sixes_range_points(rule, match, prediction):
    award = 0

    if not prediction.was_submitted():
        return award

    if not prediction.total_sixes:
        return award

    if prediction.no_pre_toss_submission():
        return award

    ts = match.first_innings_sixes + match.second_innings_sixes

    if ts == prediction.total_sixes:
        award = 300

    elif abs(ts - prediction.total_sixes) == 1:
        award = 100

    elif abs(ts - prediction.total_sixes) == 2:
        award = 50

    return award * rule.points_or_factor


calculation = lambda: total_sixes_range_points(rule, match, prediction)
