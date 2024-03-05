from fixtures.models import Match, Tournament


def run():
    tournament = Tournament.objects.get(id=5)
    for match in Match.objects.filter(tournament=tournament).order_by("match_date"):
        old_name = match.name

        if (
            "Eliminator" not in old_name
            and "Qualifier" not in old_name
            and "Final" not in old_name
        ):

            new_number = ""
            for i in old_name:
                if i.isnumeric():
                    new_number = new_number + i
                    match.match_number = int(new_number)
        else:
            match.match_number = 0

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
