# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def unique_winner_runner_up(ms):
    ts = set()
    ts.add(ms.field_value("tournament_winning_team"))
    ts.add(ms.field_value("runner_up"))

    return len(ts) == 2


def error_message_function(member_submission):
    return "Please select different Teams for Winner and Runner up."


calculation = lambda: unique_winner_runner_up(member_submission)
