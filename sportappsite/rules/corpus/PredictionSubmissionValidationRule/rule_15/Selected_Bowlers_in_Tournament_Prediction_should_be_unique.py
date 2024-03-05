# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def selected_players_are_unique(ms, var_string):
    player_selection = {k: v for k, v in ms.players().items() if var_string in k}
    return len(set(player_selection.values())) == 2


def error_message_function(member_submission):
    return "Please select different players for Top Bowler One and Two fields."


calculation = lambda: selected_players_are_unique(member_submission, "bowler")
