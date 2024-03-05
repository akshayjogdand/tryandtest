# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 3

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def wicket_range_points(prediction, match):
    if not prediction.was_submitted():
        return 0

    if prediction.no_pre_toss_submission():
        return 0

    tw = match.first_innings_wickets + match.second_innings_wickets

    if tw == prediction.total_wickets:
        return 300

    elif abs(tw - prediction.total_wickets) == 1:
        return 100

    elif abs(tw - prediction.total_wickets) == 2:
        return 50

    return 0


calculation = lambda: wicket_range_points(prediction, match)
