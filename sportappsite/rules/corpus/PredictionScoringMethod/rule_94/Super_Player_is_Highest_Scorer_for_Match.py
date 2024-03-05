# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 2
rule_category = 4

# TEST
apply_to_match_type = 3

variables = ("rule", "prediction", "match_player_scores", "match")

enable_for_matches = lambda match: True


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def chose_highest_scorer_as_super_player(rule, prediction, match_player_scores):
    if prediction.super_player and prediction.super_player == highest_scoring_player(
        match_player_scores
    ):
        return rule.points_or_factor * prediction.super_player_score
    else:
        return 0


calculation = (
    lambda: chose_highest_scorer_as_super_player(rule, prediction, match_player_scores)
    if match.match_result == 0
    else 0
)
