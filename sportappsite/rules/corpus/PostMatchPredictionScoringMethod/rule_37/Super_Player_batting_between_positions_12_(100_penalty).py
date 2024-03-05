# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "prediction")

enable_for_matches = lambda match: True


def position_between(position, start, end):
    return position >= start and position <= end


def super_player_not_between(rule, prediction, start_pos, end_pos):
    if prediction.super_player is None:
        return 0

    bp = prediction.batting_performance(prediction.super_player)
    if bp is None:
        return 0

    if position_between(bp.position, start_pos, end_pos):
        return rule.points_or_factor
    else:
        return 0


calculation = lambda: super_player_not_between(rule, prediction, 1, 2)
