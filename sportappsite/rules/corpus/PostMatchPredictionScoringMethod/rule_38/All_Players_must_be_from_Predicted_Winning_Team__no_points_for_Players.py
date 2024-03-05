# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def penalize_for_players_not_in_predicted_winning_team(
    prediction, match, match_player_scores
):
    if prediction.predicted_winning_team is None:
        return 0

    points_deducted = 0

    for player_var, player in prediction.player_set_vars().items():
        if player is not None:
            if player.team(match) != prediction.predicted_winning_team:
                if player in match_player_scores:
                    points_deducted = points_deducted + abs(
                        match_player_scores[player].total_score
                    )

                    if player == prediction.super_player:
                        points_deducted = points_deducted + abs(
                            match_player_scores[player].total_score
                        )

    return -1 * points_deducted


calculation = lambda: penalize_for_players_not_in_predicted_winning_team(
    prediction, match, match_player_scores
)
