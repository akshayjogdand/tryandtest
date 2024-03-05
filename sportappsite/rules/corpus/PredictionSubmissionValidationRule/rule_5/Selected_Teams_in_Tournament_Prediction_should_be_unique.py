# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def selected_teams_are_unique(ms, var_string):
    if ms.tournament.bi_lateral:
        return True

    ts = set()
    ts.add(ms.field_value("top_team_one"))
    ts.add(ms.field_value("top_team_two"))
    ts.add(ms.field_value("top_team_three"))
    ts.add(ms.field_value("top_team_four"))
    return len(ts) == 4


def error_message_function(member_submission):
    return "Please select different Teams for Team 1, Team 2, Team 3 and 4."


calculation = lambda: selected_teams_are_unique(member_submission, "team")
