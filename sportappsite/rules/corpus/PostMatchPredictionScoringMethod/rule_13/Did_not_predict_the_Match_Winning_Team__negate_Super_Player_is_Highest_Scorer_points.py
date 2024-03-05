# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 2
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("match", "rule", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    highest_scorers = []
    highest_score = 0
    for player_score in sorted_scores:
        if player_score.total_score >= highest_score:
            highest_scorers.append(player_score.player)
            highest_score = player_score.total_score

    return highest_scorers


def negate_chose_highest_scorer_as_super_player(rule, prediction, match_player_scores):
    if prediction.super_player and prediction.super_player in highest_scoring_player(
        match_player_scores
    ):
        return rule.points_or_factor * prediction.super_player_score * -1
    else:
        return 0


calculation = (
    lambda: negate_chose_highest_scorer_as_super_player(
        rule, prediction, match_player_scores
    )
    if match.winning_team.team != prediction.predicted_winning_team
    else 0
)
