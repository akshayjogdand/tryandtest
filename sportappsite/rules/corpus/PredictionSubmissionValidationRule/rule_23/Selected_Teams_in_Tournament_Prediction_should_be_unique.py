# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def selected_teams_are_unique(ms, var_string):
    return len(set(ms.teams().values())) == 5


def error_message_function(member_submission):
    return "Please select different Teams for Winner, Runner up, Team 3 and 4."


calculation = lambda: selected_teams_are_unique(member_submission, "team")
