# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def lowest_two_batting_positions(batting_performances, players_to_penalise):
    perfs = []
    for b in batting_performances:
        if b and b.player in players_to_penalise:
            perfs.append(b)

    pos_sorted = sorted(perfs, key=lambda i: i.position)

    ranked = []
    if len(pos_sorted) == 3:
        ranked = pos_sorted[-2:]
    elif len(pos_sorted) == 2:
        ranked = pos_sorted[-1:]

    return [b.player for b in ranked]


def calculate_penalty(prediction, match, match_player_scores):
    penalty = 0
    to_penalise = []

    for var, player in prediction.player_set_vars().items():
        if player is not None:
            if player.team(match) == prediction.predicted_winning_team:
                to_penalise.append(player)

    if len(to_penalise) > 1:
        for player in lowest_two_batting_positions(
            prediction.batting_performances(), to_penalise
        ):
            if (
                player in match_player_scores
                and match_player_scores[player].total_score > 0
            ):
                penalty = penalty + match_player_scores[player].total_score

                if prediction.super_player == player:
                    penalty = penalty + match_player_scores[player].total_score

                    # Negate Super Player is highest score for the Match
                    # Needs to be removed when 2x bonus for Super Player is highest scorer is not there
                    if player == highest_scoring_player(match_player_scores):
                        penalty = penalty + (
                            match_player_scores[player].total_score * 2
                        )

    return penalty * -1


calculation = lambda: calculate_penalty(prediction, match, match_player_scores)
