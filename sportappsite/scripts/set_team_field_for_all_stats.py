from django.db import transaction

from stats.models import (
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
    PlayerScores,
)


@transaction.atomic
def run(*args):
    for klass in [
        BattingPerformance,
        BowlingPerformance,
        FieldingPerformance,
        MatchPerformance,
        PlayerScores,
    ]:
        for o in klass.objects.all():
            o.team = o.player.team(o.match)
            o.save()
