tid = 56
t = Tournament.objects.get(id=tid)
print(t)

Properties.objects.filter(
    match__in=[m for m in Match.objects.filter(tournament=t)]
).delete()
Properties.objects.filter(tournament=t).delete()

Match.objects.filter(tournament=t).delete()

PlayerTournamentHistory.objects.filter(tournament=t).delete()

Squad.objects.filter(tournament=t).delete()

ControlledGroupSubmissionsConfig.objects.filter(tournament=t).delete()
GroupSubmissionsConfig.objects.filter(tournament=t).delete()

TournamentDefaultRules.objects.filter(tournament=t).delete()

t.delete()
