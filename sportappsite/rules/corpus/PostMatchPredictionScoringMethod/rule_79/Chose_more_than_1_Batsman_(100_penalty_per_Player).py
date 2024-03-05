# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


BATSMAN = 1


def batsmen(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    return [p for p in played if p.tournament_skill(match.tournament) == BATSMAN]


def batsmen_penalty(rule, match, prediction, match_player_scores):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    all_batsmen = batsmen(match, prediction)
    how_many = len(all_batsmen)

    if how_many <= 1:
        return 0
    elif how_many == 2:
        return rule.points_or_factor
    elif how_many == 3:
        return rule.points_or_factor * 2


calculation = lambda: batsmen_penalty(rule, match, prediction, match_player_scores)
