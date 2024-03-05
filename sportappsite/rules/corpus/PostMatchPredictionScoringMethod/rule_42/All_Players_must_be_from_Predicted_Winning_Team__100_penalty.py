# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("rule", "prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def total_penalty_for_players_not_in_predicted_winning_team(
    prediction, match, match_player_scores, rule
):
    if prediction.predicted_winning_team is None:
        return 0

    players = []

    for player_var, player in prediction.player_set_vars().items():
        if player is not None and player in match_player_scores:
            if player.team(match) != prediction.predicted_winning_team:
                players.append(player)

    return len(players) * rule.points_or_factor


calculation = lambda: total_penalty_for_players_not_in_predicted_winning_team(
    prediction, match, match_player_scores, rule
)
