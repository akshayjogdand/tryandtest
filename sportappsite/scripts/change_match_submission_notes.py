from django.db import transaction

from fixtures.models import Tournament
from predictions.models import GroupSubmissionsConfig
from configurations.models import ConfigItem


@transaction.atomic
def run(tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    text = ConfigItem.objects.get(name="match_prediction_notes_text").value
    for g in GroupSubmissionsConfig.objects.filter(
        tournament=tournament,
        submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
    ):
        g.submission_notes = text
        g.save()
        print("Text changed in: {}".format(g))
