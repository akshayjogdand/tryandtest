# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 2
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


def position_between(position, start, end):
    return position >= start and position <= end


def super_player_not_between(prediction, start_pos, end_pos, rule):
    if prediction.super_player is None:
        return 0

    bp = prediction.batting_performance(prediction.super_player)
    if bp is None:
        return 0

    if position_between(bp.position, start_pos, end_pos):
        if match_player_scores[prediction.super_player].total_score > 0:
            return (
                abs(match_player_scores[prediction.super_player].total_score)
                * -1
                * rule.points_or_factor
            )
        else:
            return 0
    else:
        return 0


calculation = lambda: super_player_not_between(prediction, 1, 2, rule)
