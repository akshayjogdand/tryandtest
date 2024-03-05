# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "member_submission", "previous_submission")

enable_for_matches = lambda match: match.post_toss_changes_allowed == True


def validate_with_no_pre_toss_submission(member_submission):
    players = member_submission.players()

    if len(players) != 1:
        member_submission.validation_errors = (
            "You can only choose one Player after toss as you have no pre-toss submission. "
            "Please refresh the page to view updated data."
        )
        return False

    if players.get("super_player") is not None:
        member_submission.validation_errors = (
            "You cannot choose a Super Player after the toss."
        )
        return False

    if not member_submission.has_only_teams_or_players():
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    return True


def verify_post_toss_player_changes(member_submission, pre_toss_submission, playing_xi):
    old_player_set = set(pre_toss_submission.players().values())
    old_sp = pre_toss_submission.field_value("super_player")
    number_of_old_players = len(old_player_set)

    new_player_set = set(member_submission.players().values())
    new_sp = member_submission.field_value("super_player")
    new_players = [
        pval
        for pvar, pval in member_submission.players().items()
        if pvar != "super_player"
    ]

    eligible_super_players = set([p for p in old_player_set if p in playing_xi])

    sp_change_allowed = len(eligible_super_players) > 0
    player_change_allowed = (
        len(old_player_set.intersection(playing_xi)) != number_of_old_players
    )

    changed_players = new_player_set - old_player_set

    if None in changed_players:
        changed_players.remove(None)
    player_changes = len(changed_players)

    c = Counter([p for p in new_players if p is not None])
    new_player_tally = c.values()
    new_players_unique = len([c for c in new_player_tally if c > 1]) == 0

    # no changes detected
    if new_player_set == old_player_set and new_sp == old_sp:
        # A combination of logic and UI bugs needs this check.
        # UI: P1 = SP, P1 not in Playing XI, P2 is chosen as P1 replacement (P2 selected twice) BUT
        #    SP is blank and allowed to submit [bug 1]
        #    the form submits P1 as SP even on a blank selection [bug 2]
        #
        # Logic: this unholy fuckup therefore means:
        #     old_player_set = P1, P2, P3
        #     new_player_set is also = P1 (by bug 2), P2 (P2 selected twice), P3
        #     old_sp = P1
        #     new_sp is also = P1 (by bug 2)
        #
        # Hence uniqueness check is needed to reject the Submission.
        if not new_players_unique:
            m = "Please select different Players for Player One, Two and Three fields."
            return False, m

        return True, None

    #
    #
    # HACK -- if all 3 Players not in P-XI, web frontend UI correctly disables P2, P3 and SP;
    #         BUT it submits old pre-toss values for P2, P3 and SP as well as valid P1 choice!!!!!
    #
    #         This hack accepts the Submission.
    #
    #         This situation most likely does not affect normal Player scoring --
    #         however it might impact penalties of all sorts as the bad pre-toss values of P2, P3, SP
    #         will be recorded in the Prediction.
    #
    #
    #
    number_of_old_players_missing = len(old_player_set.difference(set(playing_xi)))
    all_old_players_missing = number_of_old_players_missing == number_of_old_players

    if player_change_allowed and player_changes == 1 and all_old_players_missing:
        return True, None

    #
    #
    if player_change_allowed and new_players_unique is False:
        m = "Please select different Players for Player One, Two and Three fields."
        return False, m

    if player_change_allowed and player_changes > 1:
        m = "Only 1 Player change allowed after the toss."
        return False, m

    if (
        player_change_allowed
        and player_changes == 1
        and len(changed_players.intersection(playing_xi)) == 0
    ):
        m = "Player not in Playing IX, change not allowed."
        return False, m

    if not player_change_allowed and player_changes > 0:
        m = "No changes allowed after toss as all Players in your orignal selection are playing."
        return False, m

    if sp_change_allowed and new_sp not in eligible_super_players:
        if len(eligible_super_players) == 1:
            m = f"You can only choose {eligible_super_players.pop().name} as your Super Player after toss."
        else:
            m = f'Super Player can only be changed to one of: {", ".join([p.name for p in eligible_super_players])} after toss.'
        return False, m

    if not sp_change_allowed and new_sp is not None:
        m = f"All Players in your orginal selection are not playing, Super Player change not allowed."
        return False, m

    return True, None


def is_post_toss_submission_valid(member_submission, last_pre_toss_submission):
    playing_eleven = member_submission.match.playing_eleven()

    # Check 1
    if len(playing_eleven) < 22:
        member_submission.validation_errors = "Please wait for Playing XI from both Teams to be announced; try in 2 minutes."
        return False

    # Check 2
    if last_pre_toss_submission is None:
        return validate_with_no_pre_toss_submission(member_submission)

    # Check 3
    if member_submission.are_non_team_non_player_values_different(
        last_pre_toss_submission
    ):
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    # Check 4
    if member_submission.are_teams_different(last_pre_toss_submission):
        member_submission.validation_errors = "Team changes are not allowed post-toss."
        return False

    # Check 5
    result, message = verify_post_toss_player_changes(
        member_submission, last_pre_toss_submission, playing_eleven
    )
    if not result:
        member_submission.validation_errors = message

    return result


def error_message_function(member_submission):
    return member_submission.validation_errors


#
# zzz
calculation = lambda: is_post_toss_submission_valid(
    member_submission, previous_submission
)
