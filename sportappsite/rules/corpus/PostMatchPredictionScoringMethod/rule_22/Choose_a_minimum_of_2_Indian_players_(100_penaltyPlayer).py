# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("match", "rule", "prediction")

enable_for_matches = lambda match: True


INDIA = 1


def non_indian_penalty(match, rule, prediction):
    non_indians = 0
    playing_xi = match.playing_eleven()
    players = prediction.player_set_vars().values()
    for p in players:
        if p is not None:
            if p.country.id != INDIA and p in playing_xi:
                non_indians = non_indians + 1

    if non_indians > 1:
        return rule.points_or_factor * (non_indians - 1)
    else:
        return 0


calculation = lambda: non_indian_penalty(match, rule, prediction)
