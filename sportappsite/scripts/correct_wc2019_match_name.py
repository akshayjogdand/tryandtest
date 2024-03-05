from fixtures.models import Match, Tournament


def run(match_number):
    tournament = Tournament.objects.get(id=5)
    match = Match.objects.get(tournament=tournament, match_number=match_number)
    old_name = match.name
    if match.team_one and match.team_two:
        new_name = "{}, {}: {} vs {}".format(
            match.tournament.name,
            match.reference_name,
            match.team_one.team.name,
            match.team_two.team.name,
        )
    else:
        new_name = "{}, {}".format(match.tournament, match.reference_name)

    match.name = new_name
    print(
        "Changing {}\nfrom: {}\nto: {}\nmatch number is: {}\n".format(
            match, old_name, new_name, match.match_number
        )
    )

    match.save()
