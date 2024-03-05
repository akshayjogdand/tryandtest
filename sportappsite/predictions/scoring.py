from collections import namedtuple

from members.models import MemberGroupRules, GroupLeaderBoard

from fixtures.models import Match

from scoring.utils import get_or_score_match_player_performances

from scoring.scoring import run_rule

from members.scoring import create_leaderboard

from rules.models import (
    GroupPredictionScoringResult,
    GroupPostMatchPredictionScoringMethodResult,
    GroupLeaderBoardScoringMethodResult,
    GroupPredictionSubmissionValidationResult,
    GroupPredictionScoringMethod,
)

from .models import (
    MemberPrediction,
    PredictionScores,
    PostPredictionScores,
    LeaderBoardScores,
    MemberSubmission,
)

import logging

logger = logging.getLogger("rules_execution")

ScoringMethods = namedtuple(
    "ScoringMethods",
    [
        "prediction_scoring_methods",
        "post_prediction_scoring_methods",
        "leaderboard_scoring_methods",
    ],
)


# TODO -- try using a Q object for this
def allowed_methods(match, methods):
    allowed = []

    for method in methods:
        method_match_tester = eval(method.enable_for_matches, {})

        if method_match_tester(match):
            allowed.append(method)

    return allowed


def apply_submission_validation_rules(
    member_submission, submission_type, tournament_format
):
    methods = list(
        MemberGroupRules.objects.filter(member_group=member_submission.member_group)
        .first()
        .group_submission_validation_rules.filter(
            is_enabled=True,
            apply_to_submission_type=submission_type,
            apply_to_match_type=tournament_format,
        )
    )

    methods = allowed_methods(member_submission.match, methods)

    inputs = {
        "match": member_submission.match,
        "member_submission": member_submission,
    }

    if (
        submission_type == MemberSubmission.MATCH_DATA_SUBMISSION
        and member_submission.match.post_toss_changes_allowed
    ):
        pre_toss_submissions = MemberSubmission.objects.filter(
            member=member_submission.member,
            match=member_submission.match,
            member_group=member_submission.member_group,
            is_post_toss=False,
            is_valid=True,
        ).order_by("-id")

        if pre_toss_submissions.exists():
            previous_submission = pre_toss_submissions.first()
        else:
            previous_submission = None

        inputs.update({"previous_submission": previous_submission})

    errors = []

    for method in methods:
        inputs.update({"rule": method})

        result = run_rule(method, inputs, GroupPredictionSubmissionValidationResult)
        result.save()
        if result.result is False:
            errors.append(result.error_message)

    return errors


def get_abandoned_rule(member_group):
    pred_methods = list(
        MemberGroupRules.objects.filter(member_group=member_group)
        .first()
        .group_prediction_scoring_rules.filter(is_enabled=True)
    )

    for m in pred_methods:
        if m.parent_rule.id == 38:
            return m


def clear_old_results(prediction):
    # clear old results
    if prediction.prediction_scores is not None:
        scores = prediction.prediction_scores
        [o.delete() for o in scores.detailed_scoring.all()]
        scores.total_score = 0
        scores.save()

    if prediction.post_prediction_scores is not None:
        pp_scores = prediction.post_prediction_scores
        [o.delete() for o in pp_scores.detailed_scoring.all()]
        pp_scores.total_score = 0
        pp_scores.save()

    if prediction.leaderboard_scores is not None:
        l_scores = prediction.leaderboard_scores
        [o.delete() for o in l_scores.detailed_scoring.all()]
        l_scores.total_score = 0
        l_scores.save()

    prediction.total_prediction_score = 0


def apply_abandoned_match_points(match, prediction):
    scores = PredictionScores()
    scores.save()

    method = get_abandoned_rule(prediction.member_group)

    inputs = {"match": match, "rule": method}

    logger.debug(f"Scoring MemberPrediction ID={prediction.id}")
    result = run_rule(method, inputs, GroupPredictionScoringResult)
    result.save()

    prediction.total_prediction_score = result.result

    scores.detailed_scoring.add(result)
    scores.total_score = float(result.result)

    scores.save()
    prediction.prediction_scores = scores


def apply_winning_team_scores(match, prediction):
    if match.winning_team:
        prediction.winning_team = match.winning_team.team
        prediction.winning_team_score = match.winning_score
        prediction.winning_team_calculated_winning_score = (
            match.calculated_winning_score
        )
        prediction.winning_team_final_winning_score = match.final_winning_score


def apply_player_scoring(match, prediction, match_player_scores):
    prediction.total_prediction_score = 0.0
    for player_var, player in prediction.player_set_vars().items():
        # 'player_one', player_one

        # Could be no player chosen....
        if player:
            player_score = match_player_scores.get(player)

            # Player has been chosen and has a score.
            if player_score:
                setattr(
                    prediction,
                    prediction.player_vars_to_player_scores_vars()[player_var],
                    player_score,
                )

                # i.e. prediction.player_one_score  = player_score
                prediction.total_prediction_score = (
                    prediction.total_prediction_score + player_score.total_score
                )

                if player == prediction.super_player:
                    prediction.super_player_score = player_score.total_score

            # Player has been chosen but has no score
            else:
                setattr(
                    prediction,
                    prediction.player_vars_to_player_scores_vars()[player_var],
                    None,
                )

        # no player chosen
        else:
            setattr(
                prediction,
                prediction.player_vars_to_player_scores_vars()[player_var],
                None,
            )


def apply_post_prediction_scoring(
    match, prediction, match_player_scores, scoring_methods
):
    # clear old results
    if prediction.post_prediction_scores is not None:
        scores = prediction.post_prediction_scores
        [o.delete() for o in scores.detailed_scoring.all()]
        scores.total_score = 0
        scores.save()

    else:
        scores = PostPredictionScores()
        scores.save()

    inputs = {
        "match": match,
        "prediction": prediction,
        "match_player_scores": match_player_scores,
    }

    for method in scoring_methods:
        inputs.update({"rule": method})

        logger.debug(f"Scoring MemberPrediction ID={prediction.id}")
        result = run_rule(method, inputs, GroupPostMatchPredictionScoringMethodResult)

        result.save()

        prediction.total_prediction_score = prediction.total_prediction_score + float(
            result.result
        )

        scores.detailed_scoring.add(result)
        scores.total_score = scores.total_score + float(result.result)

    scores.save()
    prediction.post_prediction_scores = scores


def apply_prediction_scoring(match, prediction, match_player_scores, scoring_methods):

    # clear old results
    if prediction.prediction_scores is not None:
        scores = prediction.prediction_scores
        [o.delete() for o in scores.detailed_scoring.all()]
        scores.total_score = 0
        scores.save()

    else:
        scores = PredictionScores()
        scores.save()

    inputs = {
        "match": match,
        "prediction": prediction,
        "match_player_scores": match_player_scores,
    }

    for method in scoring_methods:
        inputs.update({"rule": method})

        logger.debug(f"Scoring MemberPrediction ID={prediction.id}")
        result = run_rule(method, inputs, GroupPredictionScoringResult)
        result.save()

        prediction.total_prediction_score = prediction.total_prediction_score + float(
            result.result
        )

        scores.detailed_scoring.add(result)
        scores.total_score = scores.total_score + float(result.result)

    scores.save()
    prediction.prediction_scores = scores


def apply_leaderboard_scoring(
    match, prediction, previous_leaderboard, current_leaderboard, scoring_methods
):
    # clear old results
    if prediction.leaderboard_scores is not None:
        scores = prediction.leaderboard_scores
        [o.delete() for o in scores.detailed_scoring.all()]
        scores.total_score = 0
        scores.save()

    else:
        scores = LeaderBoardScores()
        scores.save()

    inputs = {
        "match": match,
        "prediction": prediction,
        "previous_leaderboard": previous_leaderboard,
        "current_leaderboard": current_leaderboard,
    }

    for method in scoring_methods:
        inputs.update({"rule": method})

        logger.debug(f"Scoring MemberPrediction ID={prediction.id}")
        result = run_rule(method, inputs, GroupLeaderBoardScoringMethodResult)
        result.save()

        prediction.total_prediction_score = prediction.total_prediction_score + float(
            result.result
        )

        scores.detailed_scoring.add(result)
        scores.total_score = scores.total_score + float(result.result)

    scores.save()
    prediction.leaderboard_scores = scores


def get_previous_leaderboards(match, member_groups):

    group_boards = dict()

    previous_match_q = Match.objects.filter(
        match_number=match.match_number - 1, tournament=match.tournament
    )

    if not previous_match_q.exists():
        return {group: None for group in member_groups}

    previous_match = previous_match_q.first()

    for group in member_groups:
        try:
            board = GroupLeaderBoard.objects.get(
                member_group=group, match=previous_match
            )
        except GroupLeaderBoard.DoesNotExist:
            board = None
        group_boards[group] = board

    return group_boards


def re_generate_leaderboards(match, group_boards):
    for group, board in group_boards.items():
        create_leaderboard(match, group, board)


def get_current_leaderboards(match, member_groups):
    group_boards = dict()

    for group in member_groups:
        try:
            board = GroupLeaderBoard.objects.filter(
                match=match, member_group=group
            ).first()
        except GroupLeaderBoard.DoesNotExist:
            board = create_leaderboard(match, group, None)
        else:
            board = create_leaderboard(match, group, board)

        group_boards[group] = board

    return group_boards


def group_predictions_by_member_group(predictions):
    grouped = dict()
    for p in predictions:
        try:
            grouped[p.member_group].append(p)
        except KeyError:
            grouped[p.member_group] = []
            grouped[p.member_group].append(p)

    return grouped


def get_scoring_methods(match, member_group):
    post_methods = list(
        MemberGroupRules.objects.filter(member_group=member_group)
        .first()
        .group_post_match_prediction_scoring_rules.filter(
            is_enabled=True, apply_to_match_type=match.match_type
        )
    )

    post_methods = allowed_methods(match, post_methods)

    pred_methods = list(
        MemberGroupRules.objects.filter(member_group=member_group)
        .first()
        .group_prediction_scoring_rules.filter(
            is_enabled=True, apply_to_match_type=match.match_type
        )
    )

    pred_methods = allowed_methods(match, pred_methods)

    leaderboard_methods = list(
        MemberGroupRules.objects.filter(member_group=member_group)
        .first()
        .group_leaderboard_scoring_rules.filter(
            is_enabled=True, apply_to_match_type=match.match_type
        )
    )

    leaderboard_methods = allowed_methods(match, leaderboard_methods)

    return {
        member_group: ScoringMethods(pred_methods, post_methods, leaderboard_methods)
    }


def score_member_predictions(match):
    group_member_predictions = group_predictions_by_member_group(
        MemberPrediction.objects.filter(match=match).all()
    )
    match_player_scores = get_or_score_match_player_performances(match, re_score=False)
    group_scoring_methods = dict()

    try:
        for member_group, predictions in group_member_predictions.items():
            group_scoring_methods.update(get_scoring_methods(match, member_group))

            for prediction in predictions:
                logger.debug(f"Scoring MemberPrediction ID={prediction.id}")

                if not prediction.was_submitted():
                    clear_old_results(prediction)
                    # logger.debug("Skipping scoring for: {}".format(prediction))
                    continue

                if match.match_result == Match.MR_ABANDONED:
                    clear_old_results(prediction)
                    apply_abandoned_match_points(match, prediction)

                else:
                    apply_winning_team_scores(match, prediction)
                    apply_player_scoring(match, prediction, match_player_scores)

                    apply_prediction_scoring(
                        match,
                        prediction,
                        match_player_scores,
                        group_scoring_methods[member_group].prediction_scoring_methods,
                    )

                    apply_post_prediction_scoring(
                        match,
                        prediction,
                        match_player_scores,
                        group_scoring_methods[
                            member_group
                        ].post_prediction_scoring_methods,
                    )

                    prediction.total_prediction_score = (
                        prediction.total_prediction_score + prediction.game_bonus
                    )

                prediction.prediction_has_been_scored = True
                prediction.save()

        # At this point all predictions have been scored.
        # Now we apply scoring methods that operate on Leader Boards.
        previous_group_boards = get_previous_leaderboards(
            match, group_member_predictions.keys()
        )

        # This is the 'current' leaderboard WITHOUT the Leader Board Scoring
        # Methods applied. Needed to run rules that work on previous
        # leaderboards, standing comparisons, etc
        current_group_boards = get_current_leaderboards(
            match, group_member_predictions.keys()
        )

        for member_group, predictions in group_member_predictions.items():
            for prediction in predictions:
                apply_leaderboard_scoring(
                    match,
                    prediction,
                    previous_group_boards[prediction.member_group],
                    current_group_boards[prediction.member_group],
                    group_scoring_methods[member_group].leaderboard_scoring_methods,
                )

                prediction.save()

        # Regenerate the Leader Boards now that final scores have been assigned
        re_generate_leaderboards(match, current_group_boards)

    except Exception as ex:
        raise ex
