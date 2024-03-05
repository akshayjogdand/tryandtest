# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


BOWLER = 2


def lowest_scoring_player(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [
        ps for ps in sorted_scores if ps.player in prediction_players
    ]
    return prediction_players_sorted[0].player


def no_bowlers(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    if len(played) != 3:
        return False

    skills = [p.tournament_skill(match.tournament) for p in played]

    return BOWLER not in skills


def penalty(match_player_scores, prediction):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    player_to_penalize = lowest_scoring_player(match_player_scores, players)
    player_score = match_player_scores[player_to_penalize].total_score

    if player_score <= 0:
        return 0

    if player_to_penalize == prediction.super_player:
        return player_score * -2
    else:
        return player_score * -1


calculation = (
    lambda: penalty(match_player_scores, prediction)
    if no_bowlers(match, prediction)
    else 0
)
