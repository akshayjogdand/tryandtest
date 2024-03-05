from django.db import transaction

from predictions.default_submission_fields_data import create_default_submission_fields
from predictions.models import GroupSubmissionsConfig

from members.models import MemberGroup
from fixtures.models import Tournament


@transaction.atomic
def run():

    t = Tournament.objects.get(id=5)
    for mg in MemberGroup.objects.all():
        for config in GroupSubmissionsConfig.objects.filter(
            tournament=t, member_group=mg
        ).all():
            config.delete()

        print("Creating for MemberGroup: " + mg.name())
        create_default_submission_fields(mg, t)
