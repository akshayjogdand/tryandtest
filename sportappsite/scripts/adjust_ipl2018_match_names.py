from fixtures.models import Match, Tournament


def run(tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    for match in Match.objects.filter(tournament=tournament):
        match.reference_name = match.name
        old_name = match.name

        if (
            "Eliminator" not in old_name
            and "Qualifier" not in old_name
            and "Final" not in old_name
        ):
            num_str = old_name.split(" ")[0]
            new_number = ""
            for i in num_str:
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
