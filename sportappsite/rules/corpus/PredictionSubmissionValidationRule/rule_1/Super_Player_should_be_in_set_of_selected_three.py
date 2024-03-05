# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "member_submission")

enable_for_matches = lambda match: match.post_toss_changes_allowed == False


def is_super_player_in_set_of_three(ms):
    player_selection = ms.players()
    super_player = player_selection.pop("super_player", None)

    if super_player is None:
        return False
    elif super_player not in player_selection.values():
        return False
    else:
        return True


def error_message_function(member_submission):
    player_selection = member_submission.players()
    player_selection.pop("super_player", None)
    return "Your Super Player must be one of: {}".format(
        ", ".join([str(p) for p in player_selection.values()])
    )


calculation = lambda: is_super_player_in_set_of_three(member_submission)
