# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def at_least_one_in_winning_team(ms, var_string):
    t_winner = ms.field("tournament_winning_team").team

    # REMOVE hack for TIE Team -- should be proper variable.
    if t_winner.id == 24:
        return True

    team_players = t_winner.tournament_players(ms.tournament)
    player_selection = {k: v for k, v in ms.players().items() if var_string in k}

    for player in player_selection.values():
        if player in team_players:
            return True

    return False


def error_message_function(member_submission):
    return "Please select at least one Player of the Tournament from your chosen Tournament Winner."


calculation = lambda: at_least_one_in_winning_team(
    member_submission, "player_of_the_tournament"
)
