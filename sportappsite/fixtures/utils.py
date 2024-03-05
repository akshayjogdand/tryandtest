import arrow
from dateutil import tz

from django_q.models import Schedule

from predictions.management.commands.convert_to_predictions import (
    convert_submissions_for_match,
)

from .models import Tournament, Match


def print_something(s):
    print("\n\t{}\n".format(s))


def ist_to_utc(date_time_string):
    ist_date_time = arrow.get(arrow.get(date_time_string).datetime, "Asia/Kolkata")
    return ist_date_time.astimezone(tz.tzutc())


def schedule_test(ist_date_time_string):
    utc_run_time = ist_to_utc(ist_date_time_string)

    Schedule.objects.create(
        func="fixtures.utils.print_something",
        args=("Test worked.",),
        name="A test schedule.",
        schedule_type=Schedule.ONCE,
        next_run=utc_run_time,
    )


def lock_tournament_submissions_schedule(tournament_id, ist_date_time_string):
    utc_time = ist_to_utc(ist_date_time_string)

    Schedule.objects.create(
        func="fixtures.utils.lock_tournament_submissions",
        args=(tournament_id,),
        name="Lock Tournament Submissions",
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def lock_match_submisisons_schedule(match_id, ist_date_time_string):
    utc_time = ist_to_utc(ist_date_time_string)

    Schedule.objects.create(
        func="fixtures.utils.lock_match_submissions",
        args=(match_id,),
        name="Lock Match Submissions, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def unlock_match_submisisons_schedule(match_id, ist_date_time_string):
    utc_time = ist_to_utc(ist_date_time_string)

    Schedule.objects.create(
        func="fixtures.utils.unlock_match_submissions",
        args=(match_id,),
        name="Un-Lock Match Submissions, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def lock_match_post_toss_changes_schedule(match_id, ist_date_time_string):
    utc_time = ist_to_utc(ist_date_time_string)

    Schedule.objects.create(
        func="fixtures.utils.lock_match_post_toss_changes",
        args=(match_id,),
        name="Lock Match Post Toss Changes, Match ID={}".format(match_id),
        schedule_type=Schedule.ONCE,
        next_run=utc_time,
    )


def lock_match_submissions(match_id):
    m = Match.objects.get(id=match_id)
    m.submissions_allowed = False
    m.post_toss_changes_allowed = True
    m.match_status = Match.LIVE
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
    m.save()
    convert_submissions_for_match(match_id)


def lock_tournament_submissions(tournament_id):
    t = Tournament.objects.get(id=tournament_id)
    t.submissions_allowed = False
    t.save()
