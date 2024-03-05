import time
import pprint
import logging
from functools import wraps

from django.db import transaction
from django.utils import timezone
from django.db.models.functions import Cast
from django.db.models import IntegerField

from fixtures.models import Tournament

from stats.models import PlayerStat, TeamStat, PredictionFieldStat

from .models import (
    MemberSubmission,
    MemberSubmissionData,
)

from sportappsite.constants import tournament_tie_team

logger = logging.getLogger("p_a_computations")

# For some reason, this tripped up on 29th Feb 2020.
WAY_BACK = timezone.now().replace(year=2005)

RANGE_STATS_KEYS = []

# PWTS is predicted_winning_team_score
PWTS_ODI_RANGE_STATS = {
    "pwts_odi_r1": ("Under 200", (0, 199)),
    "pwts_odi_r2": ("200-225", (200, 225)),
    "pwts_odi_r3": ("226-250", (226, 250)),
    "pwts_odi_r4": ("251-275", (251, 275)),
    "pwts_odi_r5": ("276-300", (276, 300)),
    "pwts_odi_r6": ("Above 300", (301, 1000)),
}

PWTS_T20_RANGE_STATS = {
    "pwts_t20_r1": ("Under 100", (0, 99)),
    "pwts_t20_r2": ("100-125", (100, 125)),
    "pwts_t20_r3": ("126-150", (126, 150)),
    "pwts_t20_r4": ("151-175", (151, 175)),
    "pwts_t20_r5": ("176-200", (176, 200)),
    "pwts_t20_r6": ("Above 200", (201, 1000)),
}

PWTS_TESTS_RANGE_STATS = {}

RANGE_STATS_KEYS.extend(PWTS_ODI_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(PWTS_T20_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(PWTS_TESTS_RANGE_STATS.keys())

# TW is total_wickets
TW_ODI_RANGE_STATS = {
    "tw_odi_r1": ("0-3", (0, 3)),
    "tw_odi_r2": ("4-7", (4, 7)),
    "tw_odi_r3": ("8-11", (8, 11)),
    "tw_odi_r4": ("12-15", (12, 15)),
    "tw_odi_r5": ("16-20", (16, 20)),
}

TW_T20_RANGE_STATS = {
    "tw_t20_r1": ("0-3", (0, 3)),
    "tw_t20_r2": ("4-7", (4, 7)),
    "tw_t20_r3": ("8-11", (8, 11)),
    "tw_t20_r4": ("12-15", (12, 15)),
    "tw_t20_r5": ("16-20", (16, 20)),
}


TW_TESTS_RANGE_STATS = {
    "tw_tests_r1": ("0-8", (0, 8)),
    "tw_tests_r2": ("9-16", (9, 16)),
    "tw_tests_r3": ("17-24", (17, 24)),
    "tw_tests_r4": ("25-32", (25, 32)),
    "tw_tests_r5": ("33-40", (33, 40)),
}

RANGE_STATS_KEYS.extend(TW_ODI_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TW_T20_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TW_TESTS_RANGE_STATS.keys())

# TF is total_fours
TF_T20_RANGE_STATS = {
    "tf_t20_r1": ("Under 20", (0, 19)),
    "tf_t20_r2": ("20-24", (20, 24)),
    "tf_t20_r3": ("25-29", (25, 29)),
    "tf_t20_r4": ("30-34", (30, 34)),
    "tf_t20_r5": ("35-39", (35, 39)),
    "tf_t20_r6": ("Above 39", (40, 1000)),
}

TF_ODI_RANGE_STATS = {
    "tf_odi_r1": ("Under 20", (0, 19)),
    "tf_odi_r2": ("20-26", (20, 26)),
    "tf_odi_r3": ("27-32", (27, 32)),
    "tf_odi_r4": ("33-38", (33, 38)),
    "tf_odi_r5": ("39-45", (39, 45)),
    "tf_odi_r6": ("Above 45", (46, 1000)),
}

TF_TESTS_RANGE_STATS = {
    "tf_tests_r1": ("Under 20", (0, 19)),
    "tf_tests_r2": ("20-26", (20, 26)),
    "tf_tests_r3": ("27-32", (27, 32)),
    "tf_tests_r4": ("33-38", (33, 38)),
    "tf_tests_r5": ("39-45", (39, 45)),
    "tf_tests_r6": ("Above 45", (46, 1000)),
}

RANGE_STATS_KEYS.extend(TF_T20_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TF_ODI_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TF_TESTS_RANGE_STATS.keys())

# TS is total_sixes
TS_T20_RANGE_STATS = {
    "ts_t20_r1": ("Under 5", (0, 4)),
    "ts_t20_r2": ("5-7", (5, 7)),
    "ts_t20_r3": ("8-10", (8, 10)),
    "ts_t20_r4": ("11-13", (11, 13)),
    "ts_t20_r5": ("14-16", (14, 16)),
    "ts_t20_r6": ("Above 16", (17, 1000)),
}

TS_ODI_RANGE_STATS = {
    "ts_odi_r1": ("Under 5", (0, 4)),
    "ts_odi_r2": ("5-8", (5, 8)),
    "ts_odi_r3": ("9-12", (9, 12)),
    "ts_odi_r4": ("13-16", (13, 16)),
    "ts_odi_r5": ("17-20", (17, 20)),
    "ts_odi_r6": ("Above 20", (21, 1000)),
}

TS_TESTS_RANGE_STATS = {
    "ts_tests_r1": ("Under 5", (0, 4)),
    "ts_tests_r2": ("5-8", (5, 8)),
    "ts_tests_r3": ("9-12", (9, 12)),
    "ts_tests_r4": ("13-16", (13, 16)),
    "ts_tests_r5": ("17-20", (17, 20)),
    "ts_tests_r6": ("Above 20", (21, 1000)),
}

RANGE_STATS_KEYS.extend(TS_T20_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TS_ODI_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(TS_TESTS_RANGE_STATS.keys())

# First innings run lead
FIRL_T20_RANGE_STATS = {}
FIRL_ODI_RANGE_STATS = {}

FIRL_TESTS_RANGE_STATS = {
    "firl_tests_r1": ("Under 50", (0, 49)),
    "firl_tests_r2": ("50-100", (50, 100)),
    "firl_tests_r3": ("101-150", (101, 150)),
    "firl_tests_r4": ("151-200", (151, 200)),
    "firl_tests_r5": ("Above 200", (201, 1000)),
}

RANGE_STATS_KEYS.extend(FIRL_ODI_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(FIRL_T20_RANGE_STATS.keys())
RANGE_STATS_KEYS.extend(FIRL_TESTS_RANGE_STATS.keys())


RANGE_STATS = (
    "predicted_winning_team_score",
    "total_wickets",
    "total_fours",
    "total_sixes",
)

RAW_NUMERIC_STATS = "win_series_margin"

TOURNAMENT_PLAYER_STATS = {
    "top_bowler_one": "selection_percentage_as_top_bowler",
    "top_bowler_two": "selection_percentage_as_top_bowler",
    "top_bowler_three": "selection_percentage_as_top_bowler",
    "top_batsman_one": "selection_percentage_as_top_batsman",
    "top_batsman_two": "selection_percentage_as_top_batsman",
    "top_batsman_three": "selection_percentage_as_top_batsman",
    "most_valuable_player_one": "selection_percentage_as_mvp",
    "most_valuable_player_two": "selection_percentage_as_mvp",
    "most_valuable_player_three": "selection_percentage_as_mvp",
    "player_of_the_tournament_one": "selection_percentage_as_player_of_tournament",
    "player_of_the_tournament_two": "selection_percentage_as_player_of_tournament",
}

TOURNAMENT_TEAM_STATS = {
    "top_team_one": "selection_percentage_as_top_team_one",
    "top_team_two": "selection_percentage_as_top_team_two",
    "top_team_three": "selection_percentage_as_top_team_three",
    "top_team_four": "selection_percentage_as_top_team_four",
    "tournament_winning_team": "selection_percentage_as_tournament_winner",
    "runner_up": "selection_percentage_as_runner_up",
}


TOURNAMENT_STATS = {
    "win_series_margin": "win_series_margin",
}

TOURNAMENT_STATS.update(TOURNAMENT_PLAYER_STATS)

TOURNAMENT_STATS.update(TOURNAMENT_TEAM_STATS)


MODEL_STAT_NAMES = {
    "player_one": "selection_percentage",
    "player_two": "selection_percentage",
    "player_three": "selection_percentage",
    "super_player": "selection_percentage_as_sp",
    "predicted_winning_team": "selection_percentage_as_winning_team",
}

NUMERIC_STAT_NAMES = {"win_series_margin": "win_series_margin"}

MODEL_STAT_NAMES.update(TOURNAMENT_STATS)

P_F_SPEC = (
    PlayerStat,
    "player",
)

S_P_SPEC = (
    PlayerStat,
    "player",
)

T_F_SPEC = (
    TeamStat,
    "team",
)


MODEL_STAT_SPECS = {
    "player_one": P_F_SPEC,
    "player_two": P_F_SPEC,
    "player_three": P_F_SPEC,
    "super_player": S_P_SPEC,
    "predicted_winning_team": T_F_SPEC,
    "top_bowler_one": P_F_SPEC,
    "top_bowler_two": P_F_SPEC,
    "top_bowler_three": P_F_SPEC,
    "top_batsman_one": P_F_SPEC,
    "top_batsman_two": P_F_SPEC,
    "top_batsman_three": P_F_SPEC,
    "most_valuable_player_one": P_F_SPEC,
    "most_valuable_player_two": P_F_SPEC,
    "most_valuable_player_three": P_F_SPEC,
    "player_of_the_tournament_one": P_F_SPEC,
    "player_of_the_tournament_two": P_F_SPEC,
    "top_team_one": T_F_SPEC,
    "top_team_two": T_F_SPEC,
    "top_team_three": T_F_SPEC,
    "top_team_four": T_F_SPEC,
    "tournament_winning_team": T_F_SPEC,
    "runner_up": T_F_SPEC,
}


ADD = 1
REMOVE = 2
COUNT = 3


def log_all_exceptions(func):
    @wraps(func)
    def trapper(*args, **kwargs):
        logger.debug(f"Calling: {func.__name__}")
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            logger.exception(ex)
            logger.error(f"{func.__name__} failed!")
            logger.error(f"ARGS: {pprint.pformat(args)}")
            logger.error(f"KWARGS: {pprint.pformat(kwargs)}")

    return trapper


def names_and_ranges(smap):
    d = []
    for k, v in smap.items():
        d.append((k, v[1], v[0]))

    return d


def stat_names_and_ranges(field_name, m_t_format):
    def predicted_winning_team_score(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return names_and_ranges(PWTS_T20_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return names_and_ranges(PWTS_ODI_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.TEST:
            return names_and_ranges(PWTS_TESTS_RANGE_STATS)

    def total_wickets(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return names_and_ranges(TW_T20_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return names_and_ranges(TW_ODI_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.TEST:
            return names_and_ranges(TW_TESTS_RANGE_STATS)

    def total_fours(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return names_and_ranges(TF_T20_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return names_and_ranges(TF_ODI_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.TEST:
            return names_and_ranges(TF_TESTS_RANGE_STATS)

    def total_sixes(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return names_and_ranges(TS_T20_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return names_and_ranges(TS_ODI_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.TEST:
            return names_and_ranges(TS_TESTS_RANGE_STATS)

    def first_innings_run_lead(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return names_and_ranges(FIRL_T20_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return names_and_ranges(FIRL_ODI_RANGE_STATS)

        elif m_t_format == PredictionFieldStat.TEST:
            return names_and_ranges(FIRL_TESTS_RANGE_STATS)

    if field_name == "total_sixes":
        return total_sixes(m_t_format)

    if field_name == "total_fours":
        return total_fours(m_t_format)

    if field_name == "total_wickets":
        return total_wickets(m_t_format)

    if field_name == "predicted_winning_team_score":
        return predicted_winning_team_score(m_t_format)

    if field_name == "first_innings_run_lead":
        return first_innings_run_lead(m_t_format)

    return []


def stat_names(field_name, m_t_format):
    def predicted_winning_team_score(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return PWTS_T20_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return PWTS_ODI_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.TEST:
            return PWTS_TESTS_RANGE_STATS.keys()

    def total_wickets(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TW_T20_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TW_ODI_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.TEST:
            return TW_TESTS_RANGE_STATS.keys()

    def total_fours(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TF_T20_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TF_ODI_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.TEST:
            return TF_TESTS_RANGE_STATS.keys()

    def total_sixes(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TS_T20_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TS_ODI_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.TEST:
            return TS_TESTS_RANGE_STATS.keys()

    def first_innings_run_lead(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return FIRL_T20_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return FIRL_ODI_RANGE_STATS.keys()

        elif m_t_format == PredictionFieldStat.TEST:
            return FIRL_TESTS_RANGE_STATS.keys()

    if field_name == "total_sixes":
        return total_sixes(m_t_format)

    if field_name == "total_fours":
        return total_fours(m_t_format)

    if field_name == "total_wickets":
        return total_wickets(m_t_format)

    if field_name == "predicted_winning_team_score":
        return predicted_winning_team_score(m_t_format)

    if field_name == "first_innings_run_lead":
        return first_innings_run_lead(m_t_format)

    if field_name in RAW_NUMERIC_STATS:
        return [NUMERIC_STAT_NAMES[field_name]]

    if field_name in MODEL_STAT_SPECS:
        return [MODEL_STAT_NAMES[field_name]]


def stat_details(field_name, field_value, m_t_format):
    def test(v, lower, upper):
        return v >= lower and v <= upper

    def predicted_winning_team_score(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return PWTS_T20_RANGE_STATS

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return PWTS_ODI_RANGE_STATS

        elif m_t_format == PredictionFieldStat.TEST:
            return PWTS_TESTS_RANGE_STATS

    def total_wickets(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TW_T20_RANGE_STATS

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TW_ODI_RANGE_STATS

        elif m_t_format == PredictionFieldStat.TEST:
            return TW_TESTS_RANGE_STATS

    def total_fours(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TF_T20_RANGE_STATS

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TF_ODI_RANGE_STATS

        elif m_t_format == PredictionFieldStat.TEST:
            return TF_TESTS_RANGE_STATS

    def total_sixes(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return TS_T20_RANGE_STATS

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return TS_ODI_RANGE_STATS

        elif m_t_format == PredictionFieldStat.TEST:
            return TS_TESTS_RANGE_STATS

    def first_innings_run_lead(m_t_format):
        if m_t_format == PredictionFieldStat.T_TWENTY:
            return FIRL_T20_RANGE_STATS

        elif m_t_format == PredictionFieldStat.ONE_DAY:
            return FIRL_ODI_RANGE_STATS

        elif m_t_format == PredictionFieldStat.TEST:
            return FIRL_TESTS_RANGE_STATS

    if field_name == "total_sixes":
        smap = total_sixes(m_t_format)

    if field_name == "total_fours":
        smap = total_fours(m_t_format)

    if field_name == "total_wickets":
        smap = total_wickets(m_t_format)

    if field_name == "predicted_winning_team_score":
        smap = predicted_winning_team_score(m_t_format)

    if field_name == "first_innings_run_lead":
        smap = first_innings_run_lead(m_t_format)

    for stat_name, (desc, ranges) in smap.items():
        if test(int(field_value), *ranges):
            return stat_name, ranges

    # Code only gets here is there is no match in the ranges.
    # Eg. Member submits total_wickets=29 for T20 -- max is 20.
    # In this case just return the last item in the range.
    # This allows some form of computation to take place and the rest of the Submission Stats to proceed computation.
    return stat_name, ranges


@log_all_exceptions
def valid_member_submission(member_submission_id, submission_type):
    # Qcluster task to process this is launched at MS being created, however validity of the submission is calculated
    # after that, i.e. some other code can set is_valid = False a few seconds later. Hence:
    # Wait for rule processing + caches and DB to catch up, can be a problems in some environments.
    time.sleep(0.5)

    member_submission = None

    s_type = "Match"
    if submission_type == MemberSubmission.TOURNAMENT_DATA_SUBMISSION:
        s_type = "Tourament"

    try:
        member_submission = MemberSubmission.objects.get(
            id=member_submission_id, is_valid=True, submission_type=submission_type
        )
    except MemberSubmission.DoesNotExist:
        logger.info(
            f"Processing {s_type} PA stats for MS.id={member_submission_id} -- valid record not found, re-trying in 3 seconds."
        )
        time.sleep(3)

        try:
            member_submission = MemberSubmission.objects.get(
                id=member_submission_id, is_valid=True, submission_type=submission_type
            )
        except MemberSubmission.DoesNotExist:
            logger.info(
                f"Processing {s_type} PA stats for MS.id={member_submission_id} -- valid record not found, giving up."
            )
        else:
            return member_submission

    else:
        return member_submission


@log_all_exceptions
def previous_member_submission(member_submission):
    base_filter = {
        "member": member_submission.member,
        "member_group": member_submission.member_group,
        "is_valid": True,
        "submission_time__range": (WAY_BACK, member_submission.submission_time),
        "submission_format": member_submission.submission_format,
    }

    if member_submission.submission_type == MemberSubmission.MATCH_DATA_SUBMISSION:
        base_filter["match"] = member_submission.match
        base_filter["submission_type"] = MemberSubmission.MATCH_DATA_SUBMISSION

    if member_submission.submission_type == MemberSubmission.TOURNAMENT_DATA_SUBMISSION:
        base_filter["tournament"] = member_submission.tournament
        base_filter["submission_type"] = MemberSubmission.TOURNAMENT_DATA_SUBMISSION

    previous_member_submissions = (
        MemberSubmission.objects.filter(**base_filter)
        .exclude(id=member_submission.id)
        .order_by("-id")
    )

    if previous_member_submissions.exists():
        return previous_member_submissions.first()


@log_all_exceptions
def find_previous_stat(
    model, stat_name, match_or_tournament, field_value, member_group
):
    logger.debug(f"mark_previous_stat(\n{pprint.pformat(locals())})")

    qf = {
        "stat_name": stat_name,
        "is_latest": True,
        "member_group": member_group,
    }

    if isinstance(match_or_tournament, Tournament):
        qf["tournament"] = match_or_tournament

    else:
        qf["match"] = match_or_tournament

    if model is PlayerStat:
        qf["player"] = field_value
        qf["team"] = field_value.team(match_or_tournament)

    elif model is TeamStat:
        qf["team"] = field_value

    elif model is PredictionFieldStat:
        if stat_name in RAW_NUMERIC_STATS:
            qf["raw_input_value"] = field_value

    logger.debug(f"Attempt fetch with qf={qf}")

    try:
        return model.objects.get(**qf)

    except model.DoesNotExist:
        logger.debug(f"{model} not found, qf={qf}")
        pass

    except model.MultipleObjectsReturned as ex:
        logger.error(f"MULTIPLE OBJECTS FOUND qf={qf}")
        raise ex


# Special case to count 'selection_percentage' player stat, selection in any of the 3 Submission fields
# in the a,b,c,d sets counts towards the stat.
@log_all_exceptions
def adjust_field_name_clause_if_needed(prediction_field_name):
    logger.debug(f"adjust_field_name_clause_if_needed(\n{pprint.pformat(locals())})")

    adjusted = {"field_name": prediction_field_name}

    # Match Prediction fields.
    a = ("player_one", "player_two", "player_three")

    # Tournament Prediction fields.
    b = ("top_bowler_one", "top_bowler_two", "top_bowler_three")
    c = ("top_batsman_one", "top_batsman_two", "top_batsman_three")
    d = (
        "most_valuable_player_one",
        "most_valuable_player_two",
        "most_valuable_player_three",
    )
    e = ("player_of_the_tournament_one", "player_of_the_tournament_two")

    for field_set in (a, b, c, d, e):
        if prediction_field_name in field_set:
            adjusted = {"field_name__in": field_set}

    return adjusted


# MSD.value is stored as a String -- need to convert
@log_all_exceptions
def adjust_data_field_attribute_if_needed(
    data_field_attribute, field_value, query_filter
):
    logger.debug(f"adjust_data_field_attribute_if_needed(\n{pprint.pformat(locals())})")

    if data_field_attribute == "value__range":
        qf = query_filter.annotate(
            int_value=Cast("value", output_field=IntegerField())
        ).filter(int_value__range=field_value)

    else:
        qf = query_filter.filter(**{data_field_attribute: field_value})

    return qf


@log_all_exceptions
def prediction_submissions_count(match_or_tournament, time_range, member_group):
    logger.debug(f"prediction_submissions_count(\n{pprint.pformat(locals())})")

    if isinstance(match_or_tournament, Tournament):
        submissions_filter = {
            "tournament": match_or_tournament,
            "is_valid": True,
            "submission_type": MemberSubmission.TOURNAMENT_DATA_SUBMISSION,
        }

    else:
        submissions_filter = {
            "match": match_or_tournament,
            "is_valid": True,
            "submission_type": MemberSubmission.MATCH_DATA_SUBMISSION,
        }

    if time_range:
        submissions_filter.update({"submission_time__range": time_range})

    submissions_filter = MemberSubmission.objects.filter(**submissions_filter)

    if member_group:
        submissions_filter = submissions_filter.filter(
            member_group=member_group
        ).distinct("member")
    else:
        submissions_filter = submissions_filter.distinct("member", "member_group")

    return submissions_filter.count()


@log_all_exceptions
# Same method as prediction_submissions_count but this does the special 2-level count for super_player.
# Assume 20 Submissions, 10 have Player X, 3 have Player X as Super Player.
# Super Player stat for Player X is:  3/10 * 100 = 30%
# Selection % as Player stat for Player X is 10/20 * 100 = 50%
# This count function does this special calculation to get the '10', prediction_submissions_count will get '20'.
def super_player_prediction_submissions_count(
    match_or_tournament, time_range, member_group, player
):
    logger.debug(f"prediction_submissions_count(\n{pprint.pformat(locals())})")

    if isinstance(match_or_tournament, Tournament):
        field_filter = {
            "member_submission__tournament": match_or_tournament,
            "member_submission__is_valid": True,
            "member_submission__submission_type": MemberSubmission.TOURNAMENT_DATA_SUBMISSION,
        }

    else:
        field_filter = {
            "member_submission__match": match_or_tournament,
            "member_submission__is_valid": True,
            "member_submission__submission_type": MemberSubmission.MATCH_DATA_SUBMISSION,
        }

    field_filter.update(adjust_field_name_clause_if_needed("player_one"))
    field_filter.update({"player": player})

    if time_range:
        field_filter.update({"member_submission__submission_time__range": time_range})

    field_filter = MemberSubmissionData.objects.filter(**field_filter)

    if member_group:
        field_filter = field_filter.filter(
            member_submission__member_group=member_group
        ).distinct("member_submission__member")

    else:
        field_filter = field_filter.distinct(
            "member_submission__member", "member_submission__member_group"
        )

    return field_filter.count()


@log_all_exceptions
def prediction_field_and_submissions_count(
    prediction_field_name,
    data_field_attribute,
    field_value,
    match_or_tournament,
    member_group,
    time_range,
):
    logger.debug(
        f"prediction_field_and_submissions_count(\n{pprint.pformat(locals())})"
    )

    if isinstance(match_or_tournament, Tournament):
        field_filter = {
            "member_submission__tournament": match_or_tournament,
            "member_submission__is_valid": True,
            "member_submission__submission_type": MemberSubmission.TOURNAMENT_DATA_SUBMISSION,
        }

    else:
        field_filter = {
            "member_submission__match": match_or_tournament,
            "member_submission__is_valid": True,
            "member_submission__submission_type": MemberSubmission.MATCH_DATA_SUBMISSION,
        }

    field_filter.update(adjust_field_name_clause_if_needed(prediction_field_name))

    if time_range:
        field_filter.update({"member_submission__submission_time__range": time_range})

    field_filter = MemberSubmissionData.objects.filter(**field_filter)
    field_filter = adjust_data_field_attribute_if_needed(
        data_field_attribute, field_value, field_filter
    )

    if member_group:
        field_filter = field_filter.filter(
            member_submission__member_group=member_group
        ).distinct("member_submission__member")

    else:
        field_filter = field_filter.distinct(
            "member_submission__member", "member_submission__member_group"
        )

    return field_filter.count()


@log_all_exceptions
def apply_stat_op(prev_stat, stat_op, submissions_count):
    logger.debug(f"apply_stat_op(\n{pprint.pformat(locals())})")

    prev_stat.is_latest = False
    prev_stat.save()

    new_stat = prev_stat
    new_stat.pk = None
    new_stat.id = None

    if stat_op == ADD:
        new_stat.inc()
    elif stat_op == REMOVE:
        new_stat.dec()

    # This is effectively COUNT i.e. total / current submissions count
    sv = (new_stat.total() / submissions_count) * 100
    new_stat.stat_value = sv
    new_stat.submission_count = submissions_count
    new_stat.calculation = f"# {sv}; ({new_stat.total()} / {submissions_count}) * 100"
    new_stat.is_latest = True
    new_stat.save()


@log_all_exceptions
def prediction_field_stat(
    field_name,
    field_value,
    match_or_tournament,
    member_group,
    member_submission,
    stat_op,
    match_or_tournament_type,
):

    # This situations can happen when certain fields we are looking for are not present in the MS, typically
    # super_player in post toss scenarios.
    if field_value is None:
        if member_submission:
            msid = f"MS.id={member_submission.id}"
        else:
            msid = "GLOBALLY"

        logger.warn(f"Not computing PA stat for {field_name}={field_value}, for {msid}")

        return

    logger.debug(f"prediction_field_stat(\n{pprint.pformat(locals())})")

    stats_and_ranges = []
    model = None

    if field_name in RANGE_STATS:
        data_field_attribute = "value__range"
        model = PredictionFieldStat

        # find the relevant stat for this field_name and value
        if field_value:
            stat_name, ranges = stat_details(
                field_name, field_value, match_or_tournament_type
            )
            stats_and_ranges.append((stat_name, ranges))

        # otherwise we need to recalculate ALL stats related to that field_name.
        # Needed for calculating PA stats for old matches, will be needed by update_final_submission_stats()
        else:
            stats_and_ranges = stat_names_and_ranges(
                field_name, match_or_tournament_type
            )

    elif field_name in MODEL_STAT_SPECS:
        model, data_field_attribute = MODEL_STAT_SPECS[field_name]
        stats_and_ranges.append((MODEL_STAT_NAMES[field_name], field_value))

    elif field_name in RAW_NUMERIC_STATS:
        model = PredictionFieldStat
        data_field_attribute = "value"
        stats_and_ranges.append((NUMERIC_STAT_NAMES[field_name], int(field_value)))

    time_range = None
    if member_submission:
        time_range = (WAY_BACK, member_submission.submission_time)

    if field_name == "super_player":
        submissions_count = super_player_prediction_submissions_count(
            match_or_tournament, time_range, member_group, field_value
        )
    else:
        submissions_count = prediction_submissions_count(
            match_or_tournament, time_range, member_group
        )

    # for some range we have just 2 value and for some 3 so adding third to make this code work as expected
    # below to this for it was showing unpack error
    for s in stats_and_ranges:
        if len(s) == 2:
            i = stats_and_ranges.index(s)
            stats_and_ranges[i] = (s[0], s[1], "")

    for stat_name, ranges, range_name in stats_and_ranges:
        previous_stat = find_previous_stat(
            model, stat_name, match_or_tournament, field_value, member_group
        )

        if previous_stat:
            # Need this check in certain cases, e.g.: top_bowler_* fields map to single stat:
            # selection_percentage_as_top_bowler. So for player X, we might have calculated 0% for
            # field=top_bowler_one, stat=selection_percentage_as_top_bowler (i.e. no previous_stat).
            # When we get to top_bowler_two for same player, a previous_stat exists. If the submissions_count is still
            # 0, this will result in a division by zero error.
            # This check guards againt it.
            if submissions_count > 0:
                apply_stat_op(previous_stat, stat_op, submissions_count)

        if not previous_stat:
            assert stat_op != REMOVE

            field_count = prediction_field_and_submissions_count(
                field_name,
                data_field_attribute,
                ranges,
                match_or_tournament,
                member_group,
                time_range,
            )

            if field_count == 0 and submissions_count == 0:
                sv = 0
            else:
                sv = (field_count / submissions_count) * 100

            if not field_value:
                fv = f"Recalculate for range {ranges[0]}-{ranges[1]}"
            elif field_name in RANGE_STATS:
                fv = f"range: {ranges}"
            else:
                fv = f"v={field_value}"

            ps = model(
                stat_name=stat_name,
                member_group=member_group,
                is_latest=True,
                stat_value=sv,
                calculation=f"# {fv}; ({field_count} / {submissions_count}) * 100",
                add_counter=field_count,
                submission_count=submissions_count,
                match_or_tournament_format=match_or_tournament_type,
            )

            if model is PlayerStat:
                ps.player = field_value
                ps.team = field_value.team(match_or_tournament)

            elif model is TeamStat:
                ps.team = field_value

            elif model is PredictionFieldStat and field_name in RAW_NUMERIC_STATS:
                ps.raw_input_value = field_value

            if isinstance(match_or_tournament, Tournament):
                ps.tournament = match_or_tournament
            else:
                ps.match = match_or_tournament

            ps.save()


@transaction.atomic
def update_match_submission_stats(member_submission_id):
    member_submission = valid_member_submission(
        member_submission_id, MemberSubmission.MATCH_DATA_SUBMISSION
    )

    if not member_submission:
        return

    logger.info(f"PA Stats MS.id={member_submission.id} :: Begin")

    previous_submission = previous_member_submission(member_submission)
    current_players = set(member_submission.players().values())
    new_sp = member_submission.field_value("super_player")
    new_team = member_submission.field_value("predicted_winning_team")

    previous_players = set()
    prev_sp = None
    prev_team = None
    new_values = member_submission.values()
    old_values = {}

    if previous_submission:
        logger.debug(
            f"MS.id={member_submission.id}:: Previous Sub: {previous_submission.id} "
        )

        previous_players = set(previous_submission.players().values())
        prev_sp = previous_submission.field_value("super_player")
        prev_team = previous_submission.field_value("predicted_winning_team")
        new_values, old_values = member_submission.value_changes(previous_submission)

        if prev_sp != new_sp:
            logger.debug(f"MS.id={member_submission.id}:: Prev sp: {prev_sp}")
            logger.debug(f"MS.id={member_submission.id}:: New sp: {new_sp}")
            # Selection of Super Players has changed.
            # Need to re-compute stat for the 2 players.
            prediction_field_stat(
                "super_player",
                prev_sp,
                member_submission.match,
                None,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )

            prediction_field_stat(
                "super_player",
                prev_sp,
                member_submission.match,
                member_submission.member_group,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )

            prediction_field_stat(
                "super_player",
                new_sp,
                member_submission.match,
                None,
                member_submission,
                ADD,
                member_submission.submission_format,
            )
            prediction_field_stat(
                "super_player",
                new_sp,
                member_submission.match,
                member_submission.member_group,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

        if prev_team != new_team:
            logger.debug(f"MS.id={member_submission.id}:: Prev team: {prev_team}")
            logger.debug(f"MS.id={member_submission.id}:: New team: {new_team}")

            prediction_field_stat(
                "predicted_winning_team",
                prev_team,
                member_submission.match,
                None,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )
            prediction_field_stat(
                "predicted_winning_team",
                prev_team,
                member_submission.match,
                member_submission.member_group,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )
            prediction_field_stat(
                "predicted_winning_team",
                new_team,
                member_submission.match,
                None,
                member_submission,
                ADD,
                member_submission.submission_format,
            )
            prediction_field_stat(
                "predicted_winning_team",
                new_team,
                member_submission.match,
                member_submission.member_group,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

    else:
        prediction_field_stat(
            "super_player",
            new_sp,
            member_submission.match,
            None,
            member_submission,
            ADD,
            member_submission.submission_format,
        )
        prediction_field_stat(
            "super_player",
            new_sp,
            member_submission.match,
            member_submission.member_group,
            member_submission,
            ADD,
            member_submission.submission_format,
        )

        prediction_field_stat(
            "predicted_winning_team",
            new_team,
            member_submission.match,
            member_submission.member_group,
            member_submission,
            ADD,
            member_submission.submission_format,
        )
        prediction_field_stat(
            "predicted_winning_team",
            new_team,
            member_submission.match,
            None,
            member_submission,
            ADD,
            member_submission.submission_format,
        )

    increment_stats_for = current_players.difference(previous_players)
    decrement_stats_for = previous_players.difference(current_players)

    logger.debug(
        f"MS.id={member_submission.id}:: Increment stats for: {increment_stats_for} "
    )
    for p in increment_stats_for:
        prediction_field_stat(
            "player_one",
            p,
            member_submission.match,
            member_submission.member_group,
            member_submission,
            ADD,
            member_submission.submission_format,
        )
        prediction_field_stat(
            "player_one",
            p,
            member_submission.match,
            None,
            member_submission,
            ADD,
            member_submission.submission_format,
        )

    logger.debug(
        f"MS.id={member_submission.id}:: Decrement stats for: {decrement_stats_for} "
    )
    for p in decrement_stats_for:
        prediction_field_stat(
            "player_one",
            p,
            member_submission.match,
            member_submission.member_group,
            member_submission,
            REMOVE,
            member_submission.submission_format,
        )
        prediction_field_stat(
            "player_one",
            p,
            member_submission.match,
            None,
            member_submission,
            REMOVE,
            member_submission.submission_format,
        )

    for field_name, field_value in new_values.items():
        logger.debug(
            f"MS.id={member_submission.id}:: New stat: {field_name} {field_value}"
        )
        if field_name in RANGE_STATS:

            if field_name not in old_values:
                prediction_field_stat(
                    field_name,
                    field_value,
                    member_submission.match,
                    None,
                    member_submission,
                    ADD,
                    member_submission.submission_format,
                )

                # Group stat
                prediction_field_stat(
                    field_name,
                    field_value,
                    member_submission.match,
                    member_submission.member_group,
                    member_submission,
                    ADD,
                    member_submission.submission_format,
                )

            # A change in field_value was detected from previous submission
            else:
                new_stat, _ = stat_details(
                    field_name, field_value, member_submission.match.match_type
                )
                old_stat, _ = stat_details(
                    field_name,
                    old_values[field_name],
                    member_submission.match.match_type,
                )

                # Only do this operation if the value yeilds a different stat name -- which indicates a range change.
                if old_stat != new_stat:
                    logger.debug(
                        f"MS.id={member_submission.id}:: Stat value change: {field_name}, {field_value}"
                    )
                    # Global stat
                    prediction_field_stat(
                        field_name,
                        field_value,
                        member_submission.match,
                        None,
                        member_submission,
                        ADD,
                        member_submission.submission_format,
                    )

                    # Group stat
                    prediction_field_stat(
                        field_name,
                        field_value,
                        member_submission.match,
                        member_submission.member_group,
                        member_submission,
                        ADD,
                        member_submission.submission_format,
                    )
                    # Global stat
                    prediction_field_stat(
                        field_name,
                        old_values[field_name],
                        member_submission.match,
                        None,
                        member_submission,
                        REMOVE,
                        member_submission.submission_format,
                    )

                    # Group stat
                    prediction_field_stat(
                        field_name,
                        old_values[field_name],
                        member_submission.match,
                        member_submission.member_group,
                        member_submission,
                        REMOVE,
                        member_submission.submission_format,
                    )

    for field_name, field_value in old_values.items():
        if field_name in RANGE_STATS:
            # Something not present in the new set, i.e. was disabled or removed in the new config.
            if field_name not in new_values:
                logger.debug(
                    f"MS.id={member_submission.id}:: New Stat: {field_name} {field_value}"
                )

                # Global stat
                prediction_field_stat(
                    field_name,
                    field_value,
                    member_submission.match,
                    None,
                    member_submission,
                    REMOVE,
                    member_submission.submission_format,
                )

                # Group stat
                prediction_field_stat(
                    field_name,
                    field_value,
                    member_submission.match,
                    member_submission.member_group,
                    member_submission,
                    REMOVE,
                    member_submission.submission_format,
                )

    update_global_match_stats(member_submission)

    if previous_submission and (new_sp != prev_sp):
        update_global_sp_stats(
            member_submission,
            (p for p in current_players if (p != new_sp and p != prev_sp)),
        )
    else:
        update_global_sp_stats(
            member_submission, (p for p in current_players if p != new_sp)
        )

    logger.info(f"PA Stats MS.id={member_submission.id} :: End")


@log_all_exceptions
def update_global_sp_stats(member_submission, players):
    for player in players:
        logger.debug(f"MS.id={member_submission.id}:: Re-calculate SP stat: {player}")
        prediction_field_stat(
            "super_player",
            player,
            member_submission.match,
            None,
            member_submission,
            COUNT,
            member_submission.submission_format,
        )

        prediction_field_stat(
            "super_player",
            player,
            member_submission.match,
            member_submission.member_group,
            member_submission,
            COUNT,
            member_submission.submission_format,
        )


@transaction.atomic
def update_final_match_submission_stats(match):
    players = match.tournament_players()
    teams = match.teams()
    member_groups = match.tournament.participating_member_groups()

    logger.info(f"COUNT operation for: {match}")

    for team in teams:
        prediction_field_stat(
            "predicted_winning_team", team, match, None, None, COUNT, match.match_type
        )

        for mg in member_groups:
            prediction_field_stat(
                "predicted_winning_team", team, match, mg, None, COUNT, match.match_type
            )

    for player in players:
        team = player.team(match)
        prediction_field_stat(
            "player_one", player, match, None, None, COUNT, match.match_type
        )
        prediction_field_stat(
            "super_player", player, match, None, None, COUNT, match.match_type
        )

        for mg in member_groups:
            prediction_field_stat(
                "player_one", player, match, mg, None, COUNT, match.match_type
            )
            prediction_field_stat(
                "super_player", player, match, mg, None, COUNT, match.match_type
            )

    for field_name in RANGE_STATS:
        # Global stat
        prediction_field_stat(
            field_name, None, match, None, None, COUNT, match.match_type
        )

        for mg in member_groups:
            # Group stat
            prediction_field_stat(
                field_name, None, match, mg, None, COUNT, match.match_type
            )


@transaction.atomic
def update_tournament_submission_stats(member_submission_id):

    member_submission = valid_member_submission(
        member_submission_id, MemberSubmission.TOURNAMENT_DATA_SUBMISSION
    )

    if not member_submission:
        return

    logger.info(f"{member_submission}")
    previous_submission = previous_member_submission(member_submission)
    current_submission_data = member_submission.all_submitted_fields_and_values()

    previous_submission_data = dict()

    if previous_submission:
        previous_submission_data = previous_submission.all_submitted_fields_and_values()

    if not previous_submission:
        for var, value in current_submission_data.items():
            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                member_submission.member_group,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                None,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

    else:
        to_add = dict_changes(current_submission_data, previous_submission_data)
        to_remove = dict_changes(previous_submission_data, current_submission_data)

        for var, value in to_add.items():
            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                member_submission.member_group,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                None,
                member_submission,
                ADD,
                member_submission.submission_format,
            )

        for var, value in to_remove.items():
            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                member_submission.member_group,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )

            prediction_field_stat(
                var,
                value,
                member_submission.tournament,
                None,
                member_submission,
                REMOVE,
                member_submission.submission_format,
            )


def dict_changes(new, old):
    changes = dict()

    for k, v in new.items():
        if k in old:
            if v != old[k]:
                changes[k] = v
        else:
            changes[k] = v

    return changes


@transaction.atomic
def tournament_stats_count(tournament_id, tournament_format):
    tournament = Tournament.objects.get(id=tournament_id)
    member_groups = tournament.participating_member_groups.filter(reserved=False).all()
    players = tournament.players()
    teams = tournament.teams()

    if tournament.bi_lateral:
        teams.add(tournament_tie_team())

    for team in teams:
        for team_stat in TOURNAMENT_TEAM_STATS:
            logger.info(f"{team} -- {team_stat}")
            # Global stat
            prediction_field_stat(
                team_stat, team, tournament, None, None, COUNT, tournament_format,
            )

            # Stat for each Member Group
            for mg in member_groups:
                logger.info(f"{team} -- {team_stat} -- {mg}")
                prediction_field_stat(
                    team_stat, team, tournament, mg, None, COUNT, tournament_format,
                )

    for player in players:
        for player_stat in TOURNAMENT_PLAYER_STATS:
            logger.info(f"{player} -- {player_stat}")
            prediction_field_stat(
                player_stat, player, tournament, None, None, COUNT, tournament_format,
            )

            for mg in member_groups:
                logger.info(f"{player} -- {player_stat} -- {mg}")
                prediction_field_stat(
                    player_stat, player, tournament, mg, None, COUNT, tournament_format,
                )

    if tournament.bi_lateral:
        for i in range(1, tournament.total_matches(tournament_format) + 1):
            prediction_field_stat(
                "win_series_margin",
                i,
                tournament,
                None,
                None,
                COUNT,
                tournament_format,
            )

            for mg in member_groups:
                prediction_field_stat(
                    "win_series_margin",
                    i,
                    tournament,
                    mg,
                    None,
                    COUNT,
                    tournament_format,
                )


def update_global_match_stats(member_submission):
    member_group = member_submission.member_group

    to_recalculate_for_group = []
    to_recalculate_globally = []

    group_filter = {
        "member_group": member_group,
        "is_latest": True,
    }
    global_filter = {
        "member_group": None,
        "is_latest": True,
    }

    group_filter["match"] = member_submission.match
    global_filter["match"] = member_submission.match

    group_count = prediction_submissions_count(
        member_submission.match, None, member_group
    )
    global_count = prediction_submissions_count(member_submission.match, None, None)

    group_filter["submission_count__lt"] = group_count
    global_filter["submission_count__lt"] = global_count

    logger.info(f"Group Count={group_count}, Global Count={global_count}")

    to_recalculate_for_group.extend(PredictionFieldStat.objects.filter(**group_filter))
    to_recalculate_for_group.extend(
        PlayerStat.objects.filter(**group_filter).exclude(
            stat_name=MODEL_STAT_NAMES["super_player"]
        )
    )
    to_recalculate_for_group.extend(TeamStat.objects.filter(**group_filter))

    to_recalculate_globally.extend(PredictionFieldStat.objects.filter(**global_filter))
    to_recalculate_globally.extend(
        PlayerStat.objects.filter(**global_filter).exclude(
            stat_name=MODEL_STAT_NAMES["super_player"]
        )
    )
    to_recalculate_globally.extend(TeamStat.objects.filter(**global_filter))

    logger.info(f"Recalculate needed for non-SP values in MS={member_submission.id}")

    logger.info(f"{len(to_recalculate_for_group)} in {member_group}.")
    for stat in to_recalculate_for_group:
        logger.debug(f"updating {stat.stat_name}")
        apply_stat_op(stat, COUNT, group_count)

    logger.info(f"{len(to_recalculate_globally)} GLOBALLY.")
    for stat in to_recalculate_globally:
        logger.debug(f"updating {stat.stat_name}")
        apply_stat_op(stat, COUNT, global_count)


def update_global_tournament_stats(member_submission):
    member_group = member_submission.member_group

    to_recalculate_for_group = []
    to_recalculate_globally = []

    group_filter = {
        "member_group": member_group,
        "is_latest": True,
    }
    global_filter = {
        "member_group": None,
        "is_latest": True,
    }

    group_filter["tournament"] = member_submission.tournament
    global_filter["tournament"] = member_submission.tournament

    group_count = prediction_submissions_count(
        member_submission.tournament, None, member_group
    )
    global_count = prediction_submissions_count(
        member_submission.tournament, None, None
    )

    group_filter["submission_count__lt"] = group_count
    global_filter["submission_count__lt"] = global_count

    logger.info(f"Group Count={group_count}, Global Count={global_count}")

    to_recalculate_for_group.extend(PredictionFieldStat.objects.filter(**group_filter))
    to_recalculate_for_group.extend(PlayerStat.objects.filter(**group_filter))
    to_recalculate_for_group.extend(TeamStat.objects.filter(**group_filter))

    to_recalculate_globally.extend(PredictionFieldStat.objects.filter(**global_filter))
    to_recalculate_globally.extend(PlayerStat.objects.filter(**global_filter))
    to_recalculate_globally.extend(TeamStat.objects.filter(**global_filter))

    logger.info(f"Recalculate needed for values not in MS={member_submission.id}")

    logger.info(f"{len(to_recalculate_for_group)} in {member_group}.")
    for stat in to_recalculate_for_group:
        apply_stat_op(stat, COUNT, group_count)

    logger.info(f"{len(to_recalculate_globally)} GLOBALLY.")
    for stat in to_recalculate_globally:
        apply_stat_op(stat, COUNT, global_count)
