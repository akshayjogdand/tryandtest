# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 4

# TEST
apply_to_match_type = 3

variables = ("prediction", "match", "rule")

enable_for_matches = lambda match: True


def calculate_penalty(prediction, match, rule):
    penalty = 0
    players = [p for p in prediction.player_set_vars().values() if p is not None]

    if len(set((map(lambda player: player.team(match), players)))) > 1:
        penalty = rule.points_or_factor

    return penalty


calculation = lambda: calculate_penalty(prediction, match, rule)
