# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = 0
rule_category = 3

# T_TWENTY
apply_to_match_type = 2

variables = ("prediction",)

enable_for_matches = lambda match: True


def position_between(position, start, end):
    return position >= start and position <= end


def position_not_between(position, start, end):
    return position < start or position > end


def at_least(results, times=1):
    return times <= len([i for i in filter(None, results)])


def batting_position_penalty(
    prediction,
    batting_performances,
    start_position=1,
    end_position=11,
    condition=position_between,
    chain_operator=any,
    times=1,
):
    if prediction.no_pre_toss_submission():
        return True

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


def score_of_player_in_lowest_batting_position(prediction):
    lowest_batting_position = 0
    lowest_position_player = None
    player_score = 0

    for bp in prediction.batting_performances():
        if bp.position >= lowest_batting_position:
            lowest_position_player = bp.player
            lowest_batting_position = bp.position

    if (
        lowest_position_player == prediction.player_one
        and prediction.player_one_score is not None
    ):
        player_score = prediction.player_one_score.total_score

    elif (
        lowest_position_player == prediction.player_two
        and prediction.player_two_score is not None
    ):
        player_score = prediction.player_two_score.total_score

    elif (
        lowest_position_player == prediction.player_three
        and prediction.player_three_score is not None
    ):
        player_score = prediction.player_three_score.total_score

    if lowest_position_player == prediction.super_player:
        player_score = player_score + prediction.super_player_score

    return player_score


def penalty_score(prediction):
    return abs(score_of_player_in_lowest_batting_position(prediction))


calculation = (
    lambda: 0
    if batting_position_penalty(
        prediction,
        prediction.batting_performances(),
        start_position=7,
        end_position=11,
        condition=position_between,
        chain_operator=at_least,
        times=1,
    )
    else (-1 * penalty_score(prediction))
)
