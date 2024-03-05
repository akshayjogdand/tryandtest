# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -4
rule_category = 4

# TEST
apply_to_match_type = 3

variables = ("rule", "prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def lowest_batting_positions(batting_performances, players_to_penalise):
    perfs = []
    for b in batting_performances:
        if b and b.player in players_to_penalise:
            perfs.append(b)

    pos_sorted = sorted(perfs, key=lambda i: i.position, reverse=True)
    return pos_sorted[0].player


def all_played(players, match_player_scores):
    return set(players) == set(match_player_scores.keys()).intersection(set(players))


def same_team(players, match):
    return len(set((map(lambda player: player.team(match), players)))) == 1


def calculate_penalty(rule, prediction, match, match_player_scores):
    penalty = 0
    players = [p for p in prediction.player_set_vars().values() if p is not None]

    # == 1 means all Players in 1 team
    if all_played(players, match_player_scores) and same_team(players, match):
        player_to_penalise = lowest_batting_positions(
            prediction.batting_performances(), players
        )
        if player_to_penalise == prediction.super_player:
            penalty = (
                abs(match_player_scores[player_to_penalise].total_score)
                * rule.points_or_factor
            )

    return penalty


calculation = lambda: calculate_penalty(rule, prediction, match, match_player_scores)
