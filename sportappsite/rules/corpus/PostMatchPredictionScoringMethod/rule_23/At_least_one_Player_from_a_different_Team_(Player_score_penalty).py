# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 4

# T_TWENTY
apply_to_match_type = 2

variables = ("prediction", "match", "match_player_scores")

enable_for_matches = lambda match: True


def lowest_scoring_player(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [
        ps for ps in sorted_scores if ps.player in prediction_players
    ]
    return prediction_players_sorted[0].player


def all_played(players, match_player_scores):
    return set(players) == set(match_player_scores.keys()).intersection(set(players))


def same_team(players, match):
    # == 1 means all Players in 1 Team
    return len(set((map(lambda player: player.team(match), players)))) == 1


def calculate_penalty(prediction, match, match_player_scores):
    penalty = 0
    players = [p for p in prediction.player_set_vars().values() if p is not None]

    if all_played(players, match_player_scores) and same_team(players, match):
        player_to_penalise = lowest_scoring_player(match_player_scores, players)
        penalty = match_player_scores[player_to_penalise].total_score

        if player_to_penalise == prediction.super_player:
            penalty = penalty * 2

    # Zero out negative points
    if penalty <= 0:
        return 0
    else:
        return penalty * -1


calculation = (
    lambda: 0
    if prediction.no_pre_toss_submission()
    else calculate_penalty(prediction, match, match_player_scores)
)
