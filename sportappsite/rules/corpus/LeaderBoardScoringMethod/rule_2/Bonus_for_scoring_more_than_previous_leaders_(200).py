# LEADERBOARD_SCORING
apply_rule_at = 4

points_or_factor = 200
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = (
    "rule",
    "match",
    "prediction",
    "previous_leaderboard",
    "current_leaderboard",
)

enable_for_matches = lambda match: True


def scored_more_this_match(
    rule, match, prediction, previous_leaderboard, current_leaderboard
):
    if not prediction.was_submitted():
        return 0

    if previous_leaderboard is None:
        return 0

    count = 0
    member_current_leaderboard_entry = current_leaderboard.entry(prediction.member)

    for group_member in previous_leaderboard.entries_above(prediction.member):
        group_member_current_leaderboard_entry = current_leaderboard.entry(group_member)
        group_member_current_prediction = prediction.get_prediction_for_match(
            match, group_member, prediction.member_group
        )

        if (
            group_member_current_prediction is not None
            and group_member_current_prediction.was_submitted()
        ):
            if (
                member_current_leaderboard_entry.this_match
                > group_member_current_leaderboard_entry.this_match
            ):
                count = count + 1

    return count * rule.points_or_factor


calculation = (
    lambda: scored_more_this_match(
        rule, match, prediction, previous_leaderboard, current_leaderboard
    )
    if match.match_result == 0
    else 0
)
