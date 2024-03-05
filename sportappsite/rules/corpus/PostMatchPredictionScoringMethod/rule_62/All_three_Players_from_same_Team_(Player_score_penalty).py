# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 4

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def odd_player(players, match):
    if len(players) == 3:
        p1, p2, p3 = players
        if p2.team(match) == p3.team(match):
            return p1
        if p1.team(match) == p3.team(match):
            return p2
        if p1.team(match) == p2.team(match):
            return p3

    elif len(players) == 2:
        p1, p2 = players
        return p2


def calculate_penalty(prediction, match, match_player_scores):
    penalty = 0
    players = [p for p in prediction.player_set_vars().values() if p is not None]

    if len(set((map(lambda player: player.team(match), players)))) > 1:
        player_to_penalise = odd_player(players, match)

        if player_to_penalise in match_player_scores:
            penalty = abs(match_player_scores[player_to_penalise].total_score)

        if player_to_penalise == prediction.super_player:
            penalty = penalty * 2

    return penalty * -1


calculation = lambda: calculate_penalty(prediction, match, match_player_scores)
