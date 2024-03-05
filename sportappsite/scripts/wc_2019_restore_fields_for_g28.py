from predictions.default_submission_fields_data import create_default_submission_fields
from members.models import MemberGroup
from fixtures.models import Tournament


def run():

    t = Tournament.objects.get(id=4)
    mg = MemberGroup.objects.get(id=28)
    create_default_submission_fields(mg, t)
