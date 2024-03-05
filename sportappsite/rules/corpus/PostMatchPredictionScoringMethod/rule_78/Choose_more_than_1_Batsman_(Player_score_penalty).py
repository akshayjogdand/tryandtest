# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


BATSMAN = 1


def only_positive(*scores):
    total = 0

    for s in score:
        if s > 0:
            total = total + s

    return total


def sorted_player_scores(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [
        ps for ps in sorted_scores if ps.player in prediction_players
    ]
    return prediction_players_sorted


def batsmen(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    return [p for p in played if p.tournament_skill(match.tournament) == BATSMAN]


def batsmen_penalty(match, prediction, match_player_scores):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    all_batsmen = batsmen(match, prediction)
    how_many = len(all_batsmen)

    if how_many <= 1:
        return 0

    scores = sorted_player_scores(match_player_scores, players)

    if how_many == 2:
        return only_positive(scores[0].total_score)

    if how_many == 3:
        return only_positive(scores[0].total_score, scores[1].total_score)


calculation = lambda: batsmen_penalty(match, prediction, match_player_scores)
