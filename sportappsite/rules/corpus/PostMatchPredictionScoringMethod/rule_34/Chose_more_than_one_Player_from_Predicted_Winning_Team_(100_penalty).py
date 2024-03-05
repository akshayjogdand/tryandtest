# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 3

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction", "match", "rule")

enable_for_matches = lambda match: True


def calculate_penalty(prediction, match, rule):
    penalty = 0
    count = 0
    playing_xi = match.playing_eleven()

    for var, player in prediction.player_set_vars().items():
        if player is not None:
            if (
                player.team(match) == prediction.predicted_winning_team
                and player in playing_xi
            ):
                count = count + 1
                if count > 1:
                    penalty = penalty + rule.points_or_factor

    return penalty


calculation = lambda: calculate_penalty(prediction, match, rule)
