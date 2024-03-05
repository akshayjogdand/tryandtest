from fixtures.models import PlayerTournamentHistory, Tournament

from django.db.models import Q


def run():
    t = Tournament.objects.get(id=6)
    # id 63 == Andre Russell, withdrawn
    all_his = PlayerTournamentHistory.objects.filter(
        tournament=t, status=PlayerTournamentHistory.PLAYER_WITHDRAWN
    )

    for pth in all_his:
        if pth.player.id != 63:
            pth.status = PlayerTournamentHistory.PLAYER_ACTIVE
            pth.date_withdrawn = None
            pth.save()
            print(pth)
