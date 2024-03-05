# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = -1

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction",)

enable_for_matches = lambda match: True


def position_between(position, start, end):
    return position >= start and position <= end


def at_most(results, times=1):
    return times >= len([i for i in filter(None, results)])


def batting_position_penalty(
    batting_performances,
    start_position=1,
    end_position=11,
    condition=position_between,
    chain_operator=any,
    times=1,
):
    condition_results = []

    for bp in batting_performances:
        # no batting performance record
        if bp is None:
            condition_results.append(True)
        # played, but did not bat
        elif bp.was_out == 3:
            condition_results.append(True)
        else:
            condition_results.append(
                condition(bp.position, start_position, end_position)
            )

    if chain_operator in [any, all]:
        return chain_operator(condition_results)
    else:
        return chain_operator(condition_results, times=times)


def total_penalty_points(prediction, start_position, end_position):
    if prediction.no_pre_toss_submission():
        return 0

    to_penalize = set()
    total_penalty = 0
    penalties = []

    prediction_players = {
        prediction.player_one: 0
        if prediction.player_one_score is None
        else prediction.player_one_score.total_score,
        prediction.player_two: 0
        if prediction.player_two_score is None
        else prediction.player_two_score.total_score,
        prediction.player_three: 0
        if prediction.player_three_score is None
        else prediction.player_three_score.total_score,
    }

    for bp in prediction.batting_performances():
        if bp is not None:
            if bp.position >= start_position and bp.position <= end_position:
                to_penalize.add(bp.player)

    scores = sorted([abs(prediction_players[player]) for player in to_penalize])

    if len(scores) == 3:
        penalties = [scores[0], scores[1]]

    if len(scores) == 2:
        penalties = [scores[0]]

    if prediction.super_player in to_penalize:
        sp_score = abs(prediction_players[prediction.super_player])
        # HACK sp_score can be equal to any other Player scores!!
        if sp_score in penalties:
            penalties.append(sp_score)

    for s in penalties:
        total_penalty = total_penalty + s

    return -1 * total_penalty


calculation = (
    lambda: 0
    if batting_position_penalty(
        prediction.batting_performances(),
        start_position=1,
        end_position=3,
        condition=position_between,
        chain_operator=at_most,
        times=1,
    )
    else (total_penalty_points(prediction, 1, 3))
)
