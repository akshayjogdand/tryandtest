# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "member_submission", "previous_submission")

enable_for_matches = lambda match: match.post_toss_changes_allowed == True


def validate_with_no_pre_toss_submission(member_submission):
    if len(member_submission.players()) != 1:
        member_submission.validation_errors = (
            "You can only choose one Player -- post toss, no pre toss Submission."
        )
        return False

    if not member_submission.has_only_teams_or_players():
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    return True


def is_post_toss_submission_valid(member_submission, last_pre_toss_submission):

    if last_pre_toss_submission is None:
        return validate_with_no_pre_toss_submission(member_submission)

    if member_submission.are_non_team_non_player_values_different(
        last_pre_toss_submission
    ):
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    old_player_selection = last_pre_toss_submission.players().values()
    playing_eleven = member_submission.match.playing_eleven()

    # New Super Player must be from original selection
    new_super_player = member_submission.field_value("super_player")
    eligible_super_players = [
        p.name for p in old_player_selection if p in playing_eleven
    ]

    if new_super_player not in eligible_super_players:
        member_submission.validation_errors = (
            "Your Super Player must be one of your original "
            "selection: {}".format(", ".join(eligible_super_players))
        )

        return False

    # Other then Super Player, only one change is allowed
    new_players = member_submission.players()
    changes = 0
    for p_var, player in last_pre_toss_submission.players().items():
        if p_var in new_players and p_var != "super_player":
            if player != new_players[p_var]:
                changes = changes + 1
    if changes > 1:
        member_submission.validation_errors = (
            "After the toss, you can make only one change in the Player Selection."
        )
        return False

    return True


def error_message_function(member_submission):
    return member_submission.validation_errors


calculation = lambda: is_post_toss_submission_valid(
    member_submission, previous_submission
)
