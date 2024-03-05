# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# TEST
apply_to_match_type = 3

variables = ("rule", "prediction", "match_player_scores")

enable_for_matches = lambda match: True


INDIA = 1


def non_indian_penalty(rule, prediction, match_player_scores):
    non_indians = []
    players = prediction.player_set_vars().values()
    for p in players:
        if p is not None:
            if p.country.id != INDIA:
                non_indians.append(p)

    if len(non_indians) > 1:
        penalty = 0
        non_indians.pop(0)

        for p in non_indians:
            if p in match_player_scores:
                penalty = penalty + abs(match_player_scores[p].total_score)
                if prediction.super_player == p:
                    penalty = penalty + abs(match_player_scores[p].total_score)

        return penalty * -1
    else:
        return 0


calculation = lambda: non_indian_penalty(rule, prediction, match_player_scores)
