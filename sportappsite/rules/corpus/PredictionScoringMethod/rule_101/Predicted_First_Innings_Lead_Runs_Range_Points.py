# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 4

# TEST
apply_to_match_type = 3

variables = ("match", "prediction")

enable_for_matches = lambda match: True


def range_points(s1, s2, prediction):
    difference = s1 - s2
    p_l = prediction.first_innings_run_lead

    if difference == p_l:
        return 400
    elif abs(difference - p_l) <= 20:
        return 100
    elif abs(difference - p_l) <= 40:
        return 50
    else:
        return 0


def lead_runs_score_range(match, prediction):
    if match.match_result not in (0, 1, 2):
        return 0

    t1, t2 = match.teams()
    t1_score = match.team_first_innings_runs(t1)
    t2_score = match.team_first_innings_runs(t2)

    if t1_score > t2_score:
        return range_points(t1_score, t2_score, prediction)

    if t2_score > t1_score:
        return range_points(t2_score, t1_score, prediction)

    return 0


calculation = lambda: lead_runs_score_range(match, prediction)
