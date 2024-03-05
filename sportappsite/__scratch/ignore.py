from functools import wraps

import logging
import pprint

from django.utils import timezone

from members.models import MemberGroup, Membership
from predictions.models import MemberSubmission, MemberSubmissionData

logger = logging.getLogger("console")


def xx():
    for m in Membership.objects.all():
        if m.active is False:
            if m.marked_inactive is None:
                print(f"Setting for: {m}")
                m.marked_inactive = timezone.now()
                m.save()


def log_all_exceptions(func):
    @wraps(func)
    def trapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            logger.exception(ex)
            logger.error(f"{func.__name__} failed!")
            logger.error(f"ARGS: {pprint.pformat(args)}")
            logger.error(f"KWARGS: {pprint.pformat(kwargs)}")

    return trapper


@log_all_exceptions
def zz(a, b, c=4):
    raise Exception()


def yy():
    guru = MemberGroup.objects.get(id=12)
    wassup = MemberGroup.objects.get(id=206)

    for ms in MemberSubmission.objects.filter(id__in=(14302,)):
        print(f"{ms}")

        for g in (guru, wassup):
            msd = MemberSubmissionData.objects.filter(member_submission=ms)

            ms.id = None
            ms.pk = None
            ms.member_group = g
            ms.save()

            for m_s_d in msd:
                m_s_d.id = None
                m_s_d.pk = None
                m_s_d.member_submission = ms
                m_s_d.save()

            print(f"{ms}")


def validate_with_no_pre_toss_submission(member_submission):
    players = member_submission.players()

    if len(players) != 1:
        member_submission.validation_errors = (
            "You can only choose one Player after toss as you have no pre-toss submission. "
            "Please refresh the page to view updated data."
        )
        return False

    if players.get("super_player") is not None:
        member_submission.validation_errors = (
            "You cannot choose a Super Player after the toss."
        )
        return False

    if not member_submission.has_only_teams_or_players():
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    return True


def verify_post_toss_player_changes(member_submission, pre_toss_submission, playing_xi):
    old_player_set = set(pre_toss_submission.players().values())
    old_sp = pre_toss_submission.field_value("super_player")
    number_of_old_players = len(old_player_set)

    new_player_set = set(member_submission.players().values())
    new_sp = member_submission.field_value("super_player")
    new_players = [
        pval
        for pvar, pval in member_submission.players().items()
        if pvar != "super_player"
    ]

    eligible_super_players = set([p for p in old_player_set if p in playing_xi])

    sp_change_allowed = len(eligible_super_players) > 0
    player_change_allowed = (
        len(old_player_set.intersection(playing_xi)) != number_of_old_players
    )

    changed_players = new_player_set - old_player_set

    if None in changed_players:
        changed_players.remove(None)
    player_changes = len(changed_players)

    new_player_tally = Counter([p for p in new_players if p is not None]).values()
    new_players_unique = len([c for c in new_player_tally if c > 1]) == 0

    # no changes detected
    if new_player_set == old_player_set and new_sp == old_sp:
        return True, None

    #
    #
    # HACK -- if all 3 Players not in P-XI, web frontend UI correctly disables P2, P3 and SP;
    #         BUT it submits old pre-toss values for P2, P3 and SP as well as valid P1 choice!!!!!
    #
    #         This hack accepts the Submission.
    #
    #         This situation most likely does not affect normal Player scoring --
    #         however it might impact penalties of all sorts as the bad pre-toss values of P2, P3, SP
    #         will be recorded in the Prediction.
    #
    #
    #
    number_of_old_players_missing = len(old_player_set.difference(set(playing_xi)))
    all_old_players_missing = number_of_old_players_missing == number_of_old_players

    if player_change_allowed and player_changes == 1 and all_old_players_missing:
        return True, None

    #
    #

    if player_change_allowed and new_players_unique is False:
        m = "Please select different Players for Player One, Two and Three fields."
        return False, m

    if player_change_allowed and player_changes > 1:
        m = "Only 1 Player change allowed after the toss."
        return False, m

    if (
        player_change_allowed
        and player_changes == 1
        and len(changed_players.intersection(playing_xi)) == 0
    ):
        m = "Player not in Playing IX, change not allowed."
        return False, m

    if not player_change_allowed and player_changes > 0:
        m = "No changes allowed after toss as all Players in your orignal selection are playing."
        return False, m

    if sp_change_allowed and new_sp not in eligible_super_players:
        if len(eligible_super_players) == 1:
            m = f"You can only choose {eligible_super_players.pop().name} as your Super Player after toss."
        else:
            m = f'Super Player can only be changed to one of: {", ".join([p.name for p in eligible_super_players])} after toss.'
        return False, m

    if not sp_change_allowed and new_sp is not None:
        m = f"All Players in your orginal selection are not playing, Super Player change not allowed."
        return False, m

    return True, None


def is_post_toss_submission_valid(member_submission, last_pre_toss_submission):
    playing_eleven = member_submission.match.playing_eleven()

    # Check 1
    if len(playing_eleven) < 22:
        member_submission.validation_errors = "Please wait for Playing XI from both Teams to be announced; try in 2 minutes."
        return False

    # Check 2
    if last_pre_toss_submission is None:
        return validate_with_no_pre_toss_submission(member_submission)

    # Check 3
    if member_submission.are_non_team_non_player_values_different(
        last_pre_toss_submission
    ):
        member_submission.validation_errors = (
            "These value changes are not allowed post-toss."
        )
        return False

    # Check 4
    if member_submission.are_teams_different(last_pre_toss_submission):
        member_submission.validation_errors = "Team changes are not allowed post-toss."
        return False

    # Check 5
    result, message = verify_post_toss_player_changes(
        member_submission, last_pre_toss_submission, playing_eleven
    )
    if not result:
        member_submission.validation_errors = message

    return result


def error_message_function(member_submission):
    return member_submission.validation_errors


def check_some_ms():
    # Nishit shah
    psid = 17259
    ps = MemberSubmission.objects.get(id=psid)
    for msid in (17280,):
        ms = MemberSubmission.objects.get(id=msid)
        x = is_post_toss_submission_valid(ms, ps)
        print(msid, "  ", x, "  ", ms.validation_errors)

    # manish babbar
    psid = 17164
    ps = MemberSubmission.objects.get(id=psid)
    for msid in (17279,):
        ms = MemberSubmission.objects.get(id=msid)
        x = is_post_toss_submission_valid(ms, ps)
        print(msid, "  ", x, "  ", ms.validation_errors)

    # pragnesh shah
    psid = 17179
    ps = MemberSubmission.objects.get(id=psid)
    for msid in (
        17281,
        17287,
        17289,
        17291,
    ):
        ms = MemberSubmission.objects.get(id=msid)
        x = is_post_toss_submission_valid(ms, ps)
        print(msid, "  ", x, "  ", ms.validation_errors)

    # shalab saxena
    psid = 17264
    ps = MemberSubmission.objects.get(id=psid)
    for msid in (
        17273,
        17276,
        17277,
        17278,
    ):
        ms = MemberSubmission.objects.get(id=msid)
        x = is_post_toss_submission_valid(ms, ps)
        print(msid, "  ", x, "  ", ms.validation_errors)

    # raghu
    psid = 17109
    ps = MemberSubmission.objects.get(id=psid)
    for msid in (17296,):
        ms = MemberSubmission.objects.get(id=msid)
        x = is_post_toss_submission_valid(ms, ps)
        print(msid, "  ", x, "  ", ms.validation_errors)


def flip_match(m):
    print(
        f"post_toss={m.post_toss_changes_allowed},  submissions_allowed={m.submissions_allowed}"
    )

    o_pt = m.post_toss_changes_allowed
    o_ms = m.submissions_allowed

    m.post_toss_changes_allowed = o_ms
    m.submissions_allowed = o_pt
    m.save()

    print(
        f"post_toss={m.post_toss_changes_allowed},  submissions_allowed={m.submissions_allowed}"
    )


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
        if prediction.super_player in to_penalize:
            sp_score = abs(prediction_players[prediction.super_player])
            # HACK sp_score can be equal to any other Player scores!!
            if sp_score in penalties:
                penalties.append(sp_score)

    for s in penalties:
        total_penalty = total_penalty + s

    return -1 * total_penalty


previous_match = Match.objects.filter(
    tournament=match.tournament,
    match_date__date__lte=match.match_date,
    match_type=Match.T_TWENTY,
    fake_match=False,
).order_by("-match_date")


# Roanuz Match key
m_id = 935
m = Match.objects.get(id=m_id)
print(m)
print(m.properties_set.first().property_value)


def wtc_reverse():
    match = Match.objects.get(id=1064)
    tournament = match.tournament

    ms = MemberSubmission.objects.filter(match=match)
    ts = MemberSubmission.objects.filter(tournament=tournament)

    for m in ms:
        print(
            f"{m.id} -- {m.member} -- {m.member_group} -- {m.converted_to_prediction}"
        )

    for m in ms:
        if m.converted_to_prediction:
            m.converted_to_prediction = False
            m.save()

    for tm in ts:
        if tm.converted_to_prediction:
            tm.converted_to_prediction = False
            tm.save()

    for pred in MemberPrediction.objects.filter(match=match):
        # print(pred)
        pred.delete()

    for tpred in MemberTournamentPrediction.objects.filter(tournament=tournament):
        tpred.delete()


from scoring.utils import get_or_score_match_player_performances

match = Match.objects.get(id=1028)
prediction = MemberPrediction.objects.get(id=370306)

BATSMAN = 1

match_player_scores = get_or_score_match_player_performances(match, re_score=False)


#########

match = Match.objects.get(id=1028)
prediction = MemberPrediction.objects.get(id=370306)

BATSMAN = 1

match_player_scores = get_or_score_match_player_performances(match, re_score=False)


match = Match.objects.get(id=1029)
prediction = MemberPrediction.objects.get(id=371066)

BATSMAN = 1

match_player_scores = get_or_score_match_player_performances(match, re_score=False)


def only_positive_scores(sorted_scores, how_many_penalties):
    penalized = 0
    scores = []

    for s in sorted_scores:
        if s.total_score > 0 and penalized < how_many_penalties:
            scores.append(s)
            penalized = penalized + 1

    return scores


def only_positive(sorted_scores, how_many_penalties):
    total = 0
    penalized = 0

    for s in sorted_scores:
        if s.total_score > 0 and penalized < how_many_penalties:
            total = total + s.total_score
            penalized = penalized + 1

    return total


def sorted_batsmen_scores(match_player_scores, prediction_players, batsmen):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [
        ps for ps in sorted_scores if ps.player in prediction_players
    ]
    return [ps for ps in prediction_players_sorted if ps.player in batsmen]


def batsmen(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    return [p for p in played if p.tournament_skill(match.tournament) == BATSMAN]


def sp_is_penalty_batsman(match, prediction, match_player_scores):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    all_batsmen = batsmen(match, prediction)
    how_many = len(all_batsmen)
    penalty = 0

    if how_many <= 1:
        return penalty

    scores = sorted_batsmen_scores(match_player_scores, players, all_batsmen)
    to_penalize = how_many - 1

    for ps in only_positive_scores(scores, to_penalize):
        if ps.player == prediction.super_player:
            penalty = ps.total_score * -2

    return penalty


def batsmen_penalty(match, prediction, match_player_scores):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    all_batsmen = batsmen(match, prediction)
    how_many = len(all_batsmen)

    if how_many <= 1:
        return 0

    scores = sorted_batsmen_scores(match_player_scores, players, all_batsmen)
    to_penalise = how_many - 1

    return only_positive(scores, to_penalise) * -1


batsmen_penalty(match, prediction, match_player_scores)
sp_is_penalty_batsman(match, prediction, match_player_scores)

#####
from scoring.utils import get_or_score_match_player_performances


def highest_scoring_player(match_player_scores):
    sorted_scores = sorted(
        match_player_scores.values(), key=lambda i: i.total_score, reverse=True
    )
    return sorted_scores[0].player


def only_positive_scores(sorted_scores, how_many_penalties):
    penalized = 0
    scores = []

    for s in sorted_scores:
        if s.total_score > 0 and penalized < how_many_penalties:
            scores.append(s)
            penalized = penalized + 1

    return scores


def sorted_player_scores(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    return [ps for ps in sorted_scores if ps.player in prediction_players]


def calculate_penalty(prediction, match, match_player_scores):
    if prediction.no_pre_toss_submission():
        return 0

    p_xi = match.playing_eleven()
    prediction_players = [
        p for p in prediction.player_set_vars().values() if p is not None and p in p_xi
    ]
    penalty = 0

    if len(set((map(lambda player: player.team(match), prediction_players)))) > 1:
        how_many = len(prediction_players)
        to_penalize = how_many - 1
        sorted_scores = sorted_player_scores(match_player_scores, prediction_players)

        for ps in only_positive_scores(sorted_scores, to_penalize):
            penalty = penalty + ps.total_score

            if ps.player == prediction.super_player:
                penalty = penalty + ps.total_score

                if player_to_penalise == highest_scoring_player(match_player_scores):
                    penalty = penalty + ps.total_score + ps.total_score

    return penalty * -1


match = Match.objects.get(id=1034)
prediction = MemberPrediction.objects.get(id=375102)
prediction = MemberPrediction.objects.get(id=375045)

match_player_scores = get_or_score_match_player_performances(match, re_score=False)

calculate_penalty(prediction, match, match_player_scores)

####

match = Match.objects.get(id=1212)
prediction = MemberPrediction.objects.get(id=453522)
match == prediction.match
match_player_scores = get_or_score_match_player_performances(match, re_score=False)

ALLROUNDERS = 0

def lowest_scoring_player(match_player_scores, prediction_players):
    sorted_scores = sorted(match_player_scores.values(), key=lambda i: i.total_score)
    prediction_players_sorted = [ps for ps in sorted_scores if ps.player in prediction_players]
    return prediction_players_sorted[0].player

def no_allrounders(match, prediction):
    playing_xi = set(match.playing_eleven())
    players = set(prediction.player_set_vars().values())
    played = playing_xi.intersection(players)

    if len(played) != 3:
        return False

    skills = [p.tournament_skill(match.tournament) for p in played]

    return ALLROUNDERS not in skills

def penalty(match_player_scores, prediction):
    players = [p for p in prediction.player_set_vars().values() if p is not None]
    print(f'{players}')
    player_to_penalize = lowest_scoring_player(match_player_scores, players)
    player_score = match_player_scores[player_to_penalize].total_score

    if player_score <= 0:
        return 0

    if player_to_penalize == prediction.super_player:
        return player_score * -2
    else:
        return player_score * -1



penalty(match_player_scores, prediction)

###
