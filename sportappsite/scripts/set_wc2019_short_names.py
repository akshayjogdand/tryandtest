from fixtures.models import Tournament, Match


def run():
    t = Tournament.objects.get(id=5)
    for match in Match.objects.filter(tournament=t).all():
        if match.team_one and match.team_two:
            match.short_display_name = "CWC 2019: {}: {} vs. {}".format(
                match.reference_name,
                match.team_one.team.abbreviation,
                match.team_two.team.abbreviation,
            )
            match.save()
