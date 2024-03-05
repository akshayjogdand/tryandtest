# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "member_submission")

enable_for_matches = lambda match: match.post_toss_changes_allowed == False


def selected_players_are_unique(ms):
    player_selection = ms.players()
    super_player = player_selection.pop("super_player", None)
    return len(set(player_selection.values())) == 3


def error_message_function(member_submission):
    return "Please select different players for Player One, Two and Three fields."


calculation = lambda: selected_players_are_unique(member_submission)
