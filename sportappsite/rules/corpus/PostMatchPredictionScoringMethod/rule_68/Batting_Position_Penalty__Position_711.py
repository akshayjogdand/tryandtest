# POST_MATCH_PREDICTION_SCORING
apply_rule_at = 3

points_or_factor = -100
rule_category = 3

# ONE_DAY
apply_to_match_type = 1

variables = ("prediction", "rule")

enable_for_matches = lambda match: True


def position_between(position, start, end):
    return position >= start and position <= end


def position_not_between(position, start, end):
    return position < start or position > end


def at_least(results, times=1):
    return times <= len([i for i in filter(None, results)])


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


calculation = (
    lambda: 0
    if batting_position_penalty(
        prediction.batting_performances(),
        start_position=7,
        end_position=11,
        condition=position_between,
        chain_operator=at_least,
        times=1,
    )
    else rule.points_or_factor
)
