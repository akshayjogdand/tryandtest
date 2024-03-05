# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


BATSMAN = 1


def only_positive(sorted_scores, how_many_penalties):
    total = 0
    penalized = 0

    for s in sorted_scores:
        if s.total_score > 0 and penalized < how_many_penalties:
            total = total + s.total_score
            penalized = penalized + 1

    return total


def sorted_batsmen_scores(match_player_scores, prediction_players, batsmen):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [
        ps for ps in sorted_scores if ps.player in prediction_players
    ]
    return [ps for ps in prediction_players_sorted if ps.player in batsmen]


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

    scores = sorted_batsmen_scores(match_player_scores, players, all_batsmen)
    to_penalise = how_many - 1

    return only_positive(scores, to_penalise) * -1


calculation = lambda: batsmen_penalty(match, prediction, match_player_scores)
