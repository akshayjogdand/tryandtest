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


def super_player_between(prediction, start_pos, end_pos):
    if prediction.super_player is None:
        return False

    bp = prediction.batting_performance(prediction.super_player)
    if bp is None:
        return False

    if position_between(bp.position, start_pos, end_pos):
        return True
    else:
        return False


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def super_player_highest_scorer_and_opener(rule, prediction, match_player_scores):
    if super_player_between(
        prediction, 1, 2
    ) and prediction.super_player == highest_scoring_player(match_player_scores):
        return (
            abs(match_player_scores[prediction.super_player].total_score)
            * -1
            * rule.points_or_factor
        )
    else:
        return 0


calculation = lambda: super_player_highest_scorer_and_opener(
    rule, prediction, match_player_scores
)
