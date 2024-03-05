from django.db import transaction

from fixtures.models import Tournament
from predictions.models import GroupSubmissionsConfig

TEXT = """
This is where you lodge Tournament level Predictions.

You need to complete this by 7th April at 7 PM IST.
Till then, change your choices as much as you like!

Please choose:

1. Tournament Winner and Runner Up teams.

2. Third and Fourth placed teams.

3. Top 3 Batsmen in the Tournament.
At least one player has to be from your selected Tournament Winner.

4. Top 3 Bowlers in the Tournament.
At least one player has to be from your Tournament Winner.
"""


@transaction.atomic
def run(tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    for g in GroupSubmissionsConfig.objects.filter(
        tournament=tournament,
        submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
    ):
        g.submission_notes = TEXT
        g.save()
