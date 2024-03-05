from fixtures.models import Team, Match, PlayerTournamentHistory, Tournament, Squad
from live_scores.models import Properties

tournament = Tournament.objects.get(id=62)
real_wi = Team.objects.get(id=20)
wi = Team.objects.get(id=92)

# for match in Match.objects.filter(tournament=tournament):
# if match.team_one == wi:
# match.team_one = real_wi
# match.save()
#
# if match.team_two == wi:
# match.team_two = real_wi
# match.save()

for pth in PlayerTournamentHistory.objects.filter(tournament=tournament):
    if pth.team == wi:
        pth.team = real_wi
        pth.save()

for s in Squad.objects.filter(tournament=tournament):
    if s.team == wi:
        s.team = real_wi
        s.save()

tournament.save()

po = Properties.objects.get(team=wi)
po.team = real_wi
po.save()

wi.delete()

###################

tournament = Tournament.objects.get(id=62)
real_au = Team.objects.get(id=10)
au = Team.objects.get(id=22)

# for match in Match.objects.filter(tournament=tournament):
# if match.team_one == au:
# match.team_one = real_au
# match.save()
#
# if match.team_two == au:
# match.team_two = real_au
# match.save()

for pth in PlayerTournamentHistory.objects.filter(tournament=tournament):
    if pth.team == au:
        pth.team = real_au
        pth.save()

for s in Squad.objects.filter(tournament=tournament):
    if s.team == au:
        s.team = real_au
        s.save()

tournament.save()

for m in MemberTournamentPrediction.objects.filter(tournament=tournament):
    if m.tournament_winning_team == au:
        m.tournament_winning_team = real_au

    if m.runner_up == au:
        m.runner_up = real_au

    if m.top_team_one == au:
        m.top_team_one = real_au

    if m.top_team_two == au:
        m.top_team_two = real_au

    if m.top_team_three == au:
        m.top_team_three = real_au

    if m.top_team_four == au:
        m.top_team_four = real_au

    if m.last_team == au:
        m.last_team = real_au

    m.save()


for ms in MemberSubmission.objects.filter(tournament=tournament):
    for msd in ms.submission_data.all():
        if msd.team == au:
            msd.team = real_au
            msd.save()


for ms in MemberSubmission.objects.filter(match__tournament=tournament):
    for msd in ms.submission_data.all():
        if msd.team == au:
            # msd.team = real_au
            # msd.save()
            print(ms)
            print(msd)


po = Properties.objects.get(tournament=tournament, team=au)
po.team = real_au
po.save()

po = Properties.objects.get(team=au)
po.delete()


au.name = "Australia DO NOT USE"
au.abbreviation = "DO NOT USE"
au.save()


### Fixup needed for au.delete() to work -- every linked reference has to be switched.

au.delete()
