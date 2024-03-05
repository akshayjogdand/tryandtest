# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = -1

# T_TWENTY
apply_to_match_type = 2

variables = ("prediction", "rule")

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


def total_penalty_points(prediction, start_position, end_position, penalty_per_player):
    if prediction.no_pre_toss_submission():
        return 0

    to_penalize = list()
    skip_penalty = False
    total_penalty = 0
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
                ## first player, don't penalize
                if skip_penalty == False:
                    ## setup next player within position to be penalized
                    skip_penalty = True
                else:
                    to_penalize.append(bp.player)

    return len(to_penalize) * penalty_per_player


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
    else (total_penalty_points(prediction, 1, 3, rule.points_or_factor))
)
