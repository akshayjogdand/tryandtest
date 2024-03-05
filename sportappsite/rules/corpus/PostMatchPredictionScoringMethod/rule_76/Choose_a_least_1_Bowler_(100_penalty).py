# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "match", "prediction")

enable_for_matches = lambda match: True


BOWLER = 2


def no_bowlers(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    if len(played) != 3:
        return False

    skills = [p.tournament_skill(match.tournament) for p in played]

    return BOWLER not in skills


calculation = lambda: rule.points_or_factor if no_bowlers(match, prediction) else 0
