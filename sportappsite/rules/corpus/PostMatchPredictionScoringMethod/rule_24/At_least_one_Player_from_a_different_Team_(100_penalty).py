# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 4

# T_TWENTY
apply_to_match_type = 2

variables = ("prediction", "match", "rule", "match_player_scores")

enable_for_matches = lambda match: True


def all_played(players, match_player_scores):
    return set(players) == set(match_player_scores.keys()).intersection(set(players))


def same_team(players, match):
    return len(set((map(lambda player: player.team(match), players)))) == 1


def calculate_penalty(prediction, match, rule, match_player_scores):
    penalty = 0
    players = [p for p in prediction.player_set_vars().values() if p is not None]

    if all_played(players, match_player_scores) and same_team(players, match):
        penalty = rule.points_or_factor

    return penalty


calculation = (
    lambda: 0
    if prediction.no_pre_toss_submission()
    else calculate_penalty(prediction, match, rule, match_player_scores)
)
