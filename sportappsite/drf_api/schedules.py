from django.db import transaction

from django.contrib.auth.models import User

from django_q.tasks import AsyncTask

from fixtures.models import Match, Tournament


from predictions.models import (
    MemberSubmission,
    GroupSubmissionsConfig,
    MemberSubmissionData,
)

from members.utils import member_memberships
from members.models import MemberGroup

import time
import logging

logger = logging.getLogger("django")


def crosspost_async(
    user, member_group, match, tournament, member_submission, submission_values
):
    mid = None
    if match:
        mid = match.id

    logger.info(f"XPOST job set for {member_submission.id}")
    AsyncTask(
        "drf_api.schedules.crosspost",
        user.id,
        member_group.id,
        mid,
        tournament.id,
        member_submission.id,
        submission_values,
    ).run()


@transaction.atomic
def crosspost(
    user_id,
    member_group_id,
    match_id,
    tournament_id,
    member_submission_id,
    submission_values,
):
    user = User.objects.get(id=user_id)
    try:
        member_submission = MemberSubmission.objects.get(id=member_submission_id)
    except MemberSubmission.DoesNotExist:
        logger.info(
            f"XPOST, fetch for MS={member_submission_id} failed; trying in 3 seconds."
        )
        time.sleep(3)
        member_submission = MemberSubmission.objects.get(id=member_submission_id)

    member_group = MemberGroup.objects.get(id=member_group_id)

    try:
        tournament = Tournament.objects.get(id=tournament_id)
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        pass

    member, memberships = member_memberships(user)

    for m in memberships:
        if m.member_group != member_group:
            logger.info(
                f"XPOST job processing for {member_submission_id}, to {m.member_group}"
            )
            tournaments = m.member_group.tournaments.all()

            if (
                member_submission.submission_type
                == GroupSubmissionsConfig.MATCH_DATA_SUBMISSION
                and match.tournament in tournaments
            ):

                copy_submission(member_submission, m.member_group, submission_values)

            elif (
                member_submission.submission_type
                == GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION
                and tournament in tournaments
            ):

                copy_submission(member_submission, m.member_group, submission_values)


def copy_submission(member_submission, to_group, submission_values):
    original_submission_id = member_submission.id

    member_submission.pk = None
    member_submission.id = None

    member_submission.member_group = to_group
    member_submission.crossposted = True
    member_submission.crossposted_from = original_submission_id
    member_submission.save()

    for field_name, (field_type, field_value) in submission_values.items():
        sd = MemberSubmissionData()
        sd.member_submission = member_submission
        sd.field_name = field_name
        sd.set_value(field_type, field_value)
        sd.save()
