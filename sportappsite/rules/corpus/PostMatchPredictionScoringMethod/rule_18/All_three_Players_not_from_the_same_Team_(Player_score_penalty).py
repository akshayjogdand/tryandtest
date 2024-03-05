# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 4

# T_TWENTY
apply_to_match_type = 2

variables = ("prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def only_positive_scores(sorted_scores, how_many_penalties):
    penalized = 0
    scores = []

    for s in sorted_scores:
        if s.total_score > 0 and penalized < how_many_penalties:
            scores.append(s)
            penalized = penalized + 1

    return scores


def sorted_player_scores(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    return [ps for ps in sorted_scores if ps.player in prediction_players]


def calculate_penalty(prediction, match, match_player_scores):
    if prediction.no_pre_toss_submission():
        return 0

    p_xi = match.playing_eleven()
    prediction_players = [
        p for p in prediction.player_set_vars().values() if p is not None and p in p_xi
    ]
    penalty = 0

    if len(set((map(lambda player: player.team(match), prediction_players)))) > 1:
        how_many = len(prediction_players)
        to_penalize = how_many - 1
        sorted_scores = sorted_player_scores(match_player_scores, prediction_players)

        for ps in only_positive_scores(sorted_scores, to_penalize):
            penalty = penalty + ps.total_score

            if ps.player == prediction.super_player:
                penalty = penalty + ps.total_score

                if ps.player == highest_scoring_player(match_player_scores):
                    penalty = penalty + ps.total_score + ps.total_score

    return penalty * -1


calculation = lambda: calculate_penalty(prediction, match, match_player_scores)
