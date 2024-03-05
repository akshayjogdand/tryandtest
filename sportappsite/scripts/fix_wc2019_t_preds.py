from fixtures.models import Tournament, Match

from predictions.models import MemberTournamentPrediction


def run():
    t = Tournament.objects.get(id=5)
    for tp in MemberTournamentPrediction.objects.filter(tournament=t):
        tp.prediction_format = Match.ONE_DAY
        tp.save()
