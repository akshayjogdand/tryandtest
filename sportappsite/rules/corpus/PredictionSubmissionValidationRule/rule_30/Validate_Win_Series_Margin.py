# MEMBER_PREDICTION_VALIDATION
apply_rule_at = 1

points_or_factor = 0
rule_category = -1

# TEST
apply_to_match_type = 3

variables = ("rule", "member_submission")

enable_for_matches = lambda match: True


def validate(ms):
    if not ms.tournament.bi_lateral:
        return True

    t_winner = ms.field("tournament_winning_team").team
    # REMOVE hack for TIE Team -- should be proper variable.
    if t_winner.id == 24:
        return True

    choice = int(ms.field("win_series_margin").field_value())
    if choice >= 0 and choice <= ms.tournament.total_matches(3):
        return True
    else:
        return False


def error_message_function(member_submission):
    max = member_submission.tournament.total_matches(3)
    return "Please enter a value between 1 and {} for Win Series Margin.".format(max)


calculation = lambda: validate(member_submission, rule)
