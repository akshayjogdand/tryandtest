# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 3

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def total_sixes_range_points(match, prediction):
    if not prediction.was_submitted():
        return 0

    if not prediction.total_sixes:
        return 0

    if prediction.no_pre_toss_submission():
        return 0

    ts = match.first_innings_sixes + match.second_innings_sixes

    if ts == prediction.total_sixes:
        return 300

    elif abs(ts - prediction.total_sixes) <= 2:
        return 100

    elif abs(ts - prediction.total_sixes) <= 4:
        return 50

    return 0


calculation = lambda: total_sixes_range_points(match, prediction)
