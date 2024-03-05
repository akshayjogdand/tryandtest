from django_q.models import Schedule

from predictions.management.commands.convert_to_predictions import (
    convert_submissions_for_match,
)

from fixtures.models import Match

from stats.management.commands.compute_player_stats import Command as PlayerStatsCommand
from live_scores.management.commands.match_details import Command as MatchDetailsCommand
from live_scores.management.commands.season_details import (
    Command as SeasonDetailsCommand,
)
from live_scores.management.commands.ball_by_ball import Command as FetchScoresCommand
from live_scores.management.commands.match_completion import (
    Command as FinishMatchCommand,
)
from scoring.management.commands.score_match import Command as ScoreMatchCommand
from predictions.management.commands.score_member_predictions import (
    Command as ScorePredictionsCommand,
)
from fixtures.management.commands.adjust_match_data import (
    Command as FixMatchDataCommand,
)


def lock_match_submisisons_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.lock_match_submissions",
        args=(match_id,),
        name="Lock Match Submissions, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def unlock_match_submisisons_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.unlock_match_submissions",
        args=(match_id,),
        name="Un-Lock Match Submissions, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def lock_match_post_toss_changes_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.lock_match_post_toss_changes",
        args=(match_id,),
        name="Lock Match Post Toss Changes, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def poll_match_details_schedule(match_key, match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.poll_match_details",
        args=(match_key,),
        name="Poll Match Details, Match Key={}, Match ID={}".format(
            match_key, match_id
        ),
        schedule_type=Schedule.MINUTES,
        minutes=2,
        repeats=15,
        next_run=utc_time,
    )


def poll_match_details_once_schedule(match_key, match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.poll_match_details",
        args=(match_key,),
        name="Poll Match Details, Match Key={}, Match ID={}".format(
            match_key, match_id
        ),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def season_details_schedule(season_key, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.season_details",
        args=(),
        kwargs={"season_key": (season_key,)},
        name="Season Details for: {}".format(season_key),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def fetch_scores_schedule(match_key, utc_time, test_match=False):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.fetch_scores",
        args=(match_key, test_match),
        name="Fetch Score for: {}".format(match_key),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def match_completion_schedule(match_key, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.match_completion",
        args=(match_key,),
        name="Match Completion for: {}".format(match_key),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def match_scoring_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.score_match",
        args=(match_id,),
        name="Score Match for: {}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def member_scoring_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.score_predictions",
        args=(match_id,),
        name="Score Predictions for: {}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def fix_match_data_schedule(t_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.fix_matches_data",
        args=(t_id,),
        name="Fixing Tournament Matches Data, t.id={}".format(t_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def player_stats_schedule(match_id, utc_time):
    Schedule.objects.create(
        func="fixtures.management.commands.schedules.player_stats",
        args=(match_id,),
        name="Player Stats",
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def lock_match_submissions(match_id):
    m = Match.objects.get(id=match_id)
    m.submissions_allowed = False
    m.post_toss_changes_allowed = True
    m.save()


def unlock_match_submissions(match_id):
    m = Match.objects.get(id=match_id)
    m.submissions_allowed = True
    m.post_toss_changes_allowed = False
    m.save()


def lock_match_post_toss_changes(match_id):
    m = Match.objects.get(id=match_id)
    m.submissions_allowed = False
    m.post_toss_changes_allowed = False
    m.match_status = Match.LIVE
    m.save()
    convert_submissions_for_match(match_id)


def poll_match_details(match_key):
    c = MatchDetailsCommand()
    c.handle(match_key)


def season_details(season_key):
    c = SeasonDetailsCommand()
    c.handle(season_key=season_key)


def fetch_scores(match_key, test_match=False):
    c = FetchScoresCommand()

    c.handle(
        match_key=[match_key],
        over_interval=5,
        start_over=1,
        end_over=20,
        redo=False,
        team=None,
        innings=1,
    )

    if test_match:
        c.handle(
            match_key=[match_key],
            over_interval=5,
            start_over=1,
            end_over=20,
            redo=False,
            team=None,
            innings=2,
        )


def match_completion(match_key):
    c = FinishMatchCommand()
    c.handle(match_key=[match_key])


def score_match(match_id):
    c = ScoreMatchCommand()
    c.handle(match_id, False, False)


def score_predictions(match_id):
    c = ScorePredictionsCommand()
    c.handle(match_id)


def fix_matches_data(t_id):
    c = FixMatchDataCommand()
    c.handle(tournament_id=t_id)


def player_stats(match_id):
    c = PlayerStatsCommand()
    c.handle(match_id, False)
