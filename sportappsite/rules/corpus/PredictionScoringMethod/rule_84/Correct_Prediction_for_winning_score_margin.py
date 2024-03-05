# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 500
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


def predicted_margin(prediction, match, rule):
    if prediction.predicted_win_margin_range is None:
        return 0

    if prediction.predicted_win_margin_range is not None:
        try:
            if int(prediction.predicted_win_margin_range) == 0:
                return 0
        except ValueError:
            pass

        x, y = prediction.predicted_win_margin_range.strip().split("-")

        if int(x) <= match.win_margin_runs and (int(x) + 5) >= match.win_margin_runs:
            return rule.points_or_factor
        else:
            return 0


calculation = lambda: predicted_margin(prediction, match, rule)
